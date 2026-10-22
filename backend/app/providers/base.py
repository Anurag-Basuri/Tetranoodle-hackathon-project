from datetime import date
from typing import Optional, List, TypeVar, Protocol, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class SearchHit(BaseModel):
    # Normalized search result from any search engine
    url: str
    title: str
    snippet: str
    published: Optional[date] = None
    provider: str = "tavily"

class LLMProvider(Protocol):
    # Contract for structured output generation across model providers
    name: str

    async def generate(
        self,
        *,
        task: str,
        messages: List[Any],
        schema: type[T],
        timeout_s: float = 30.0,
    ) -> T:
        ...

class SearchProvider(Protocol):
    # Contract for search query providers
    name: str

    async def search(
        self,
        query: str,
        *,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
    ) -> List[SearchHit]:
        ...
