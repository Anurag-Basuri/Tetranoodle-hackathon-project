from typing import List, Optional, Any, TypeVar
from pydantic import BaseModel
from app.providers.base import SearchHit
from app.domain.errors import RetryableProviderError, PermanentProviderError

T = TypeVar("T", bound=BaseModel)

class FakeLLMProvider:
    # Deterministic LLM provider mock for unit testing
    def __init__(self, name: str = "fake_llm", canned_response: Optional[Any] = None, fail_with: Optional[Exception] = None):
        self.name = name
        self.canned_response = canned_response
        self.fail_with = fail_with
        self.call_count = 0

    async def generate(
        self,
        *,
        task: str,
        messages: List[Any],
        schema: type[T],
        timeout_s: float = 30.0,
    ) -> T:
        self.call_count += 1
        if self.fail_with:
            raise self.fail_with
        if self.canned_response is not None:
            if isinstance(self.canned_response, schema):
                return self.canned_response
            if isinstance(self.canned_response, dict):
                return schema.model_validate(self.canned_response)
        # Default fallback to construct default schema instance
        return schema.model_construct()

class FakeSearchProvider:
    # Deterministic search provider mock for unit testing
    def __init__(self, name: str = "fake_search", canned_hits: Optional[List[SearchHit]] = None, fail_with: Optional[Exception] = None):
        self.name = name
        self.canned_hits = canned_hits or []
        self.fail_with = fail_with
        self.call_count = 0

    async def search(
        self,
        query: str,
        *,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
    ) -> List[SearchHit]:
        self.call_count += 1
        if self.fail_with:
            raise self.fail_with
        return self.canned_hits[:max_results]
