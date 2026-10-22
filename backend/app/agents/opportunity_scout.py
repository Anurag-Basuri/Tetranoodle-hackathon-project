import uuid
from typing import Dict, Any, List, Set
from pydantic import HttpUrl
from app.domain.enums import AgentName
from app.domain.opportunity import Candidate
from app.agents.state import ResearchState, AgentWarning
from app.agents.base import run_agent
from app.providers.search_tavily import TavilySearchProvider
from app.providers.search_brave import BraveSearchProvider
from app.providers.base import SearchHit
from app.config import get_settings

def build_search_queries(state: ResearchState) -> List[str]:
    # Construct targeted search queries from student preferences
    p = state["profile_input"]
    field = p.field_of_study or "computer science"
    level = p.degree_level_target.value if p.degree_level_target else "master"
    countries = p.target_countries or ["Germany", "Canada", "Singapore"]

    queries = []
    for country in countries:
        queries.append(f"{country} {level} {field} university scholarship funding eligibility requirements")
        queries.append(f"top university {level} in {field} {country} international student scholarships")

    # Add broad high value funding queries
    queries.append(f"fully funded {level} scholarships in {field} for international students 2026 2027")
    return queries[:6]

async def scout_opportunities_node(state: ResearchState) -> Dict[str, Any]:
    # Opportunity Scout node: explores internet to locate candidate programs and scholarships
    settings = get_settings()
    warnings: List[AgentWarning] = []

    async def execute():
        tavily = TavilySearchProvider(api_key=settings.TAVILY_API_KEY)
        brave = BraveSearchProvider(api_key=settings.BRAVE_API_KEY)
        providers = [tavily] if not settings.BRAVE_API_KEY else [tavily, brave]

        queries = build_search_queries(state)
        seen_urls: Set[str] = set()
        candidates: List[Candidate] = []

        for q in queries:
            if len(candidates) >= settings.MAX_CANDIDATES:
                break

            hits: List[SearchHit] = []
            for prov in providers:
                try:
                    hits = await prov.search(q, max_results=5)
                    if hits:
                        break
                except Exception as e:
                    continue

            for h in hits:
                clean_url = h.url.split("?")[0].rstrip("/")
                if clean_url in seen_urls:
                    continue
                seen_urls.add(clean_url)

                # Heuristic title and institution extraction
                title = h.title or "University Program"
                inst = None
                if "-" in title:
                    parts = title.split("-")
                    inst = parts[-1].strip()
                    title = "-".join(parts[:-1]).strip()
                elif "|" in title:
                    parts = title.split("|")
                    inst = parts[-1].strip()
                    title = "|".join(parts[:-1]).strip()

                candidates.append(Candidate(
                    id=uuid.uuid4(),
                    name=title[:120],
                    institution=inst[:100] if inst else None,
                    country=state["profile_input"].target_countries[0] if state["profile_input"].target_countries else None,
                    url=h.url,
                    snippet=h.snippet,
                    discovery_provider=h.provider,
                ))

        # Check candidate threshold
        if len(candidates) < settings.MIN_CANDIDATES:
            warnings.append(AgentWarning(
                agent=AgentName.SCOUT,
                scope="discovery",
                message=f"Found {len(candidates)} candidates (target was {settings.MIN_CANDIDATES}). Proceeding with available hits.",
            ))

        return {
            "candidates": candidates,
            "warnings": warnings,
        }

    def fallback(err: Exception) -> Dict[str, Any]:
        return {
            "candidates": [],
            "warnings": [AgentWarning(
                agent=AgentName.SCOUT,
                scope="global",
                message=f"Opportunity Scout search failed: {err}",
            )],
        }

    return await run_agent(AgentName.SCOUT, "global", execute, fallback)
