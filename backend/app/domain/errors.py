from typing import Any, List, Tuple


class DomainError(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND")


class MissingTokenError(DomainError):
    def __init__(self, message: str = "Missing or invalid token"):
        super().__init__(message, code="UNAUTHENTICATED")


class ActiveJobExistsError(DomainError):
    def __init__(self, message: str = "An active research job is already running for this profile"):
        super().__init__(message, code="CONFLICT")


class NotReadyError(DomainError):
    def __init__(self, message: str = "Job results are not ready yet"):
        super().__init__(message, code="NOT_READY")


class RateLimitedError(DomainError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code="RATE_LIMITED")


class ProviderError(DomainError):
    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(f"[{provider}] {message}", code="PROVIDER_ERROR")


class RetryableProviderError(ProviderError):
    def __init__(self, message: str, provider: str = "unknown", retry_after: float = 2.0):
        self.retry_after = retry_after
        super().__init__(message, provider=provider)


class PermanentProviderError(ProviderError):
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider)


class InvalidOutputError(ProviderError):
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider=provider)


class AllProvidersFailed(DomainError):
    def __init__(self, errors: List[Tuple[str, Any]]):
        self.errors = errors
        msg = f"All providers failed: {errors}"
        super().__init__(msg, code="ALL_PROVIDERS_FAILED")
