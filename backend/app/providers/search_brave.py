from typing import List, Optional
import httpx
from app.providers.base import SearchHit
from app.domain.errors import RetryableProviderError, PermanentProviderError

class BraveSearchProvider:
    # Secondary search fallback provider using Brave Search API
    def __init__(self, api_key: str):
        self.name = "brave"
        self.api_key = api_key

    async def search(
        self,
        query: str,
        *,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
    ) -> List[SearchHit]:
        if not self.api_key:
            raise PermanentProviderError("Brave search API key is not configured", provider=self.name)

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
                if res.status_code == 401:
                    raise PermanentProviderError("Invalid Brave API token", provider=self.name)
                if res.status_code != 200:
                    raise RetryableProviderError(f"Brave error status {res.status_code}", provider=self.name)

                data = res.json()
                results = data.get("web", {}).get("results", [])

                hits = []
                for item in results:
                    hits.append(SearchHit(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        snippet=item.get("description", ""),
                        provider=self.name,
                    ))
                return hits

        except httpx.RequestError as e:
            raise RetryableProviderError(f"Brave request failed: {e}", provider=self.name)
