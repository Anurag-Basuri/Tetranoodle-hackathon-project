import asyncio
from typing import List, Any, TypeVar
from pydantic import BaseModel, ValidationError
from langchain_groq import ChatGroq
from app.providers.base import LLMProvider
from app.domain.errors import RetryableProviderError, PermanentProviderError, InvalidOutputError

T = TypeVar("T", bound=BaseModel)

class GroqLLMProvider:
    # Groq high speed inference provider adapter
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b"):
        self.name = "groq"
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
            raise PermanentProviderError("Groq API key is not configured", provider=self.name)

        try:
            llm = ChatGroq(
                model=self.model_name,
                groq_api_key=self.api_key,
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(schema)

            result = await asyncio.wait_for(structured_llm.ainvoke(messages), timeout=timeout_s)
            if not isinstance(result, schema):
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
            if "429" in err_msg or "rate limit" in err_msg or "503" in err_msg or "overloaded" in err_msg:
                raise RetryableProviderError(str(e), provider=self.name, retry_after=4.0)
            if "401" in err_msg or "invalid api key" in err_msg or "404" in err_msg:
                raise PermanentProviderError(str(e), provider=self.name)
            raise RetryableProviderError(str(e), provider=self.name)
