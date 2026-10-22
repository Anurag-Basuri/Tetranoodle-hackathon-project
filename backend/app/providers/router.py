import asyncio
import time
from typing import List, Callable, Any, TypeVar, Optional, Dict, Tuple
from pydantic import BaseModel
from app.domain.errors import (
    RetryableProviderError,
    PermanentProviderError,
    InvalidOutputError,
    AllProvidersFailed,
)

T = TypeVar("T")

class CircuitBreaker:
    # Circuit breaker tracking consecutive provider outages
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}

    def is_open(self, provider_name: str) -> bool:
        fail_count = self.failures.get(provider_name, 0)
        if fail_count < self.failure_threshold:
            return False

        last_time = self.last_failure_time.get(provider_name, 0.0)
        # Check if cooldown has elapsed
        if time.time() - last_time > self.cooldown_seconds:
            # Half-open: allow one probe
            return False
        return True

    def record_success(self, provider_name: str) -> None:
        self.failures[provider_name] = 0

    def record_failure(self, provider_name: str) -> None:
        self.failures[provider_name] = self.failures.get(provider_name, 0) + 1
        self.last_failure_time[provider_name] = time.time()

# Global circuit breaker instance
global_circuit_breaker = CircuitBreaker()

# Global concurrency semaphore for LLM calls to protect free quotas
llm_semaphore = asyncio.Semaphore(2)

class ProviderResult:
    # Container for provider execution result and provenance
    def __init__(self, value: Any, provider: str):
        self.value = value
        self.provider = provider

async def call_with_fallback(
    providers: List[Any],
    operation_factory: Callable[[Any], Any],
    *,
    task: str = "general",
    validate: Optional[Callable[[Any], None]] = None,
    max_attempts: int = 2,
    timeout_s: float = 30.0,
    breaker: Optional[CircuitBreaker] = None,
) -> ProviderResult:
    # Router orchestrating primary to secondary provider failovers
    cb = breaker or global_circuit_breaker
    errors: List[Tuple[str, Any]] = []

    for provider in providers:
        p_name = getattr(provider, "name", str(provider))

        if cb.is_open(p_name):
            errors.append((p_name, "circuit_open"))
            continue

        for attempt in range(max_attempts):
            try:
                # Wrap call inside semaphore
                async with llm_semaphore:
                    coro = operation_factory(provider)
                    result = await asyncio.wait_for(coro, timeout=timeout_s)

                if validate:
                    validate(result)

                cb.record_success(p_name)
                return ProviderResult(value=result, provider=p_name)

            except RetryableProviderError as e:
                cb.record_failure(p_name)
                delay = min(e.retry_after, 10.0) if hasattr(e, "retry_after") else (attempt + 1) * 2.0
                await asyncio.sleep(delay)

            except (PermanentProviderError, InvalidOutputError) as e:
                cb.record_failure(p_name)
                errors.append((p_name, repr(e)))
                # Do not retry permanent errors on the same provider
                break

            except asyncio.TimeoutError:
                cb.record_failure(p_name)
                errors.append((p_name, f"timeout_{timeout_s}s"))

            except Exception as e:
                cb.record_failure(p_name)
                errors.append((p_name, str(e)))

        errors.append((p_name, "exhausted"))

    raise AllProvidersFailed(errors)
