import pytest
from pydantic import BaseModel
from app.providers.fakes import FakeLLMProvider
from app.providers.router import call_with_fallback, CircuitBreaker
from app.domain.errors import RetryableProviderError, PermanentProviderError, AllProvidersFailed

class DummyOutput(BaseModel):
    message: str

@pytest.mark.asyncio
async def test_router_primary_success():
    # When primary succeeds, return its result immediately
    primary = FakeLLMProvider(name="gemini", canned_response=DummyOutput(message="ok"))
    fallback = FakeLLMProvider(name="groq", canned_response=DummyOutput(message="fallback"))

    res = await call_with_fallback(
        [primary, fallback],
        lambda p: p.generate(task="test", messages=[], schema=DummyOutput),
    )
    assert res.provider == "gemini"
    assert res.value.message == "ok"
    assert primary.call_count == 1
    assert fallback.call_count == 0

@pytest.mark.asyncio
async def test_router_failover_on_permanent_error():
    # Permanent error on primary should immediately route to secondary
    primary = FakeLLMProvider(name="gemini", fail_with=PermanentProviderError("invalid key"))
    fallback = FakeLLMProvider(name="groq", canned_response=DummyOutput(message="fallback_success"))

    res = await call_with_fallback(
        [primary, fallback],
        lambda p: p.generate(task="test", messages=[], schema=DummyOutput),
    )
    assert res.provider == "groq"
    assert res.value.message == "fallback_success"
    assert primary.call_count == 1

@pytest.mark.asyncio
async def test_router_all_providers_failed():
    # If all providers fail, raise AllProvidersFailed
    primary = FakeLLMProvider(name="gemini", fail_with=PermanentProviderError("fail1"))
    fallback = FakeLLMProvider(name="groq", fail_with=PermanentProviderError("fail2"))

    with pytest.raises(AllProvidersFailed):
        await call_with_fallback(
            [primary, fallback],
            lambda p: p.generate(task="test", messages=[], schema=DummyOutput),
        )

def test_circuit_breaker_logic():
    # Breaker should open after reaching threshold of consecutive failures
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=60.0)
    assert cb.is_open("gemini") is False

    cb.record_failure("gemini")
    cb.record_failure("gemini")
    assert cb.is_open("gemini") is False

    cb.record_failure("gemini")
    assert cb.is_open("gemini") is True

    # Reset on success
    cb.record_success("gemini")
    assert cb.is_open("gemini") is False
