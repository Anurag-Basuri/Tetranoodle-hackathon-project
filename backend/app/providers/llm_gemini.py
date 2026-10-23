import asyncio
from typing import List, Any, TypeVar
from pydantic import BaseModel, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from app.providers.base import LLMProvider
from app.domain.errors import RetryableProviderError, PermanentProviderError, InvalidOutputError

T = TypeVar("T", bound=BaseModel)

class GeminiLLMProvider:
    # Gemini model adapter with structured output support
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.name = "gemini"
        self.api_key = api_key
        self.model_name = model_name

    async def generate(
        self,
        *,
        task: str,
        messages: List[Any],
        schema: type[T],
        timeout_s: float = 30.0,
    ) -> T:
        if not self.api_key:
            raise PermanentProviderError("Gemini API key is not configured", provider=self.name)

        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(schema)

            # Enforce task timeout
            result = await asyncio.wait_for(structured_llm.ainvoke(messages), timeout=timeout_s)
            if not isinstance(result, schema):
                # Attempt manual validation if dictionary returned
                if isinstance(result, dict):
                    result = schema.model_validate(result)
                else:
                    raise InvalidOutputError(f"Unexpected output type: {type(result)}", provider=self.name)
            return result

        except asyncio.TimeoutError:
            raise RetryableProviderError(f"Timeout after {timeout_s}s", provider=self.name, retry_after=2.0)
        except ValidationError as e:
            raise InvalidOutputError(f"Output schema validation error: {e}", provider=self.name)
        except Exception as e:
            err_msg = str(e).lower()
            if "503" in err_msg or "unavailable" in err_msg or "rate limit" in err_msg or "429" in err_msg:
                raise RetryableProviderError(str(e), provider=self.name, retry_after=5.0)
            if "401" in err_msg or "403" in err_msg or "invalid api key" in err_msg:
                raise PermanentProviderError(str(e), provider=self.name)
            # Default to retryable for transient network issues
            raise RetryableProviderError(str(e), provider=self.name)
