from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import httpx
from app.domain.profile import Project

def extract_github_username(url_or_user: str) -> Optional[str]:
    # Extract username from GitHub profile URL or direct username
    if not url_or_user:
        return None
    cleaned = url_or_user.strip()
    if "/" in cleaned:
        parsed = urlparse(cleaned)
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if parts:
            return parts[0]
    return cleaned

async def fetch_github_profile(
    url_or_user: str,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    # Enrich student profile by fetching public repositories and skills
    username = extract_github_username(url_or_user)
    if not username:
        return {"skills": [], "projects": [], "warning": "Invalid GitHub username"}

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ScholarPilot-AI",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    skills: List[str] = []
    projects: List[Project] = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch user bio and basic details
            user_url = f"https://api.github.com/users/{username}"
            user_res = await client.get(user_url, headers=headers)

            if user_res.status_code == 404:
                return {"skills": [], "projects": [], "warning": f"GitHub user '{username}' not found"}
            if user_res.status_code in (403, 429):
                return {"skills": [], "projects": [], "warning": "GitHub API rate limit exceeded"}

            # Fetch top repositories
            repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=15"
            repos_res = await client.get(repos_url, headers=headers)

            if repos_res.status_code == 200:
                repos_data = repos_res.json()
                for repo in repos_data:
                    # Ignore forked repos to capture original student work
                    if repo.get("fork"):
                        continue

                    name = repo.get("name", "")
                    desc = repo.get("description") or f"Repository {name}"
                    lang = repo.get("language")
                    html_url = repo.get("html_url")

                    repo_skills = []
                    if lang and lang not in repo_skills:
                        repo_skills.append(lang)
                        if lang not in skills:
                            skills.append(lang)

                    # Extract topics/tags
                    topics = repo.get("topics", [])
                    for t in topics:
                        if t not in repo_skills:
                            repo_skills.append(t)
                        if t not in skills:
                            skills.append(t)

                    projects.append(Project(
                        name=name,
                        summary=desc,
                        skills=repo_skills,
                        url=html_url,
                        evidence=f"github.com/{username}/{name}",
                    ))

        return {
            "skills": skills[:15],
            "projects": projects[:5],
            "warning": None,
        }

    except Exception as e:
        return {
            "skills": [],
            "projects": [],
            "warning": f"GitHub enrichment failed: {e}",
        }
