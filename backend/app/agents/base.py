import asyncio
import time
from typing import Callable, Awaitable, Any, Optional
from app.domain.enums import AgentName
from app.domain.errors import RetryableProviderError

async def run_agent(
    agent_name: AgentName,
    scope: str,
    operation: Callable[[], Awaitable[Any]],
    fallback_factory: Optional[Callable[[Exception], Any]] = None,
    max_retries: int = 2,
    timeout_s: float = 90.0,
) -> Any:
    # Execution wrapper providing per agent timeout, retries, and graceful degradation
    start_time = time.time()
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            # Enforce agent timeout
            result = await asyncio.wait_for(operation(), timeout=timeout_s)
            return result

        except asyncio.TimeoutError as e:
            last_error = e
            if attempt < max_retries:
                await asyncio.sleep((attempt + 1) * 2.0)
                continue

        except RetryableProviderError as e:
            last_error = e
            if attempt < max_retries:
                delay = getattr(e, "retry_after", 3.0)
                await asyncio.sleep(min(delay, 10.0))
                continue

        except Exception as e:
            last_error = e
            # Non retryable errors break out immediately to fallback
            break

    # If fallback factory provided, return degraded result
    if fallback_factory and last_error:
        return fallback_factory(last_error)

    # Re-raise if no graceful fallback configured
    if last_error:
        raise last_error
    raise RuntimeError(f"Agent {agent_name} terminated without result")
