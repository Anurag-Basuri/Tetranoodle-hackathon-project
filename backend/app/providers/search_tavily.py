import asyncio
from typing import List, Optional
from tavily import TavilyClient
from app.providers.base import SearchHit
from app.domain.errors import RetryableProviderError, PermanentProviderError

class TavilySearchProvider:
    # Primary web search provider using Tavily API
    def __init__(self, api_key: str):
        self.name = "tavily"
        self.api_key = api_key

    async def search(
        self,
        query: str,
        *,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
    ) -> List[SearchHit]:
        if not self.api_key:
            raise PermanentProviderError("Tavily API key is not configured", provider=self.name)

        try:
            client = TavilyClient(api_key=self.api_key)
            kwargs = {
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            }
            if include_domains:
                kwargs["include_domains"] = include_domains

            # Run synchronous client search in thread pool
            res = await asyncio.to_thread(client.search, **kwargs)

            hits = []
            for item in res.get("results", []):
                hits.append(SearchHit(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("content", ""),
                    provider=self.name,
                ))
            return hits

        except Exception as e:
            err_msg = str(e).lower()
            if "invalid api key" in err_msg or "unauthorized" in err_msg:
                raise PermanentProviderError(str(e), provider=self.name)
            raise RetryableProviderError(str(e), provider=self.name)
