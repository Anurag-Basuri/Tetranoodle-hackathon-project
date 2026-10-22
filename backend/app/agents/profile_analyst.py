from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.domain.enums import AgentName, DegreeLevel
from app.domain.profile import StudentProfile, Project
from app.agents.state import ResearchState, AgentWarning
from app.agents.base import run_agent
from app.tools.github import fetch_github_profile
from app.providers.router import call_with_fallback
from app.config import get_settings

class DocumentExtractionOutput(BaseModel):
    # LLM extraction shape for uploaded resumes or marksheets
    skills: List[str] = []
    projects: List[str] = []
    achievements: List[str] = []
    identified_institution: Optional[str] = None
    missing_items: List[str] = []

async def analyze_profile_node(state: ResearchState) -> Dict[str, Any]:
    # Profile Analyst node: ingests form, uploaded docs, and enriches via GitHub
    input_profile = state["profile_input"]
    docs = state.get("documents", [])
    settings = get_settings()
    warnings: List[AgentWarning] = []

    async def execute():
        # Start with a copy of form input
        profile_data = input_profile.model_dump()
        provenance: Dict[str, str] = {k: "form" for k, v in profile_data.items() if v}
        missing_info: List[str] = list(input_profile.missing_information)

        # 1. GitHub Enrichment
        if input_profile.github_url:
            gh_result = await fetch_github_profile(
                str(input_profile.github_url),
                token=settings.GITHUB_TOKEN or None,
            )
            if gh_result.get("warning"):
                warnings.append(AgentWarning(
                    agent=AgentName.PROFILE,
                    scope="github",
                    message=gh_result["warning"],
                ))
            else:
                # Merge discovered skills and projects
                current_skills = set(profile_data.get("skills", []))
                for s in gh_result.get("skills", []):
                    if s not in current_skills:
                        current_skills.add(s)
                        provenance[f"skill:{s}"] = "github"
                profile_data["skills"] = list(current_skills)

                current_projects = list(input_profile.projects)
                for p in gh_result.get("projects", []):
                    current_projects.append(p)
                    provenance[f"project:{p.name}"] = "github"
                profile_data["projects"] = current_projects

        # 2. Document Text Extraction via LLM
        all_doc_text = "\n\n".join([f"--- Document: {d['filename']} ({d['kind']}) ---\n{d['text']}" for d in docs if d.get("text")])
        if all_doc_text:
            from app.providers.llm_gemini import GeminiLLMProvider
            from app.providers.llm_groq import GroqLLMProvider

            gemini = GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
            groq = GroqLLMProvider(api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL)

            prompt = (
                f"Extract skills, projects, achievements, institution name, and missing application documents "
                f"from this student's uploaded records:\n\n{all_doc_text[:4000]}"
            )
            messages = [{"role": "user", "content": prompt}]

            try:
                res = await call_with_fallback(
                    [gemini, groq],
                    lambda p: p.generate(task="profile_extraction", messages=messages, schema=DocumentExtractionOutput),
                )
                doc_ext: DocumentExtractionOutput = res.value

                # Merge extracted document info
                for s in doc_ext.skills:
                    if s not in profile_data["skills"]:
                        profile_data["skills"].append(s)
                        provenance[f"skill:{s}"] = "document"

                for p_name in doc_ext.projects:
                    profile_data["projects"].append(Project(
                        name=p_name,
                        summary="Extracted from student records",
                        skills=[],
                        url=None,
                        evidence="uploaded document",
                    ))

                for ach in doc_ext.achievements:
                    if ach not in profile_data["achievements"]:
                        profile_data["achievements"].append(ach)

                if not profile_data.get("institution") and doc_ext.identified_institution:
                    profile_data["institution"] = doc_ext.identified_institution
                    provenance["institution"] = "document"

                missing_info.extend(doc_ext.missing_items)

            except Exception as e:
                warnings.append(AgentWarning(
                    agent=AgentName.PROFILE,
                    scope="document_extraction",
                    message=f"Document parsing degraded: {e}",
                ))

        # Check for essential missing details
        if not input_profile.language_tests:
            if "English language test score (IELTS/TOEFL)" not in missing_info:
                missing_info.append("English language test score (IELTS/TOEFL)")

        profile_data["missing_information"] = missing_info
        profile_data["provenance"] = provenance

        return {
            "profile": StudentProfile.model_validate(profile_data),
            "warnings": warnings,
        }

    # Fallback factory returns input profile on critical agent failure
    def fallback(err: Exception) -> Dict[str, Any]:
        return {
            "profile": input_profile,
            "warnings": [AgentWarning(
                agent=AgentName.PROFILE,
                scope="global",
                message=f"Profile Analyst degraded to form input: {err}",
            )],
        }

    return await run_agent(AgentName.PROFILE, "global", execute, fallback)
