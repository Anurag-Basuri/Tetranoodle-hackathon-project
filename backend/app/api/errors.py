from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.domain.errors import (
    DomainError,
    NotFoundError,
    MissingTokenError,
    ActiveJobExistsError,
    ConflictError,
    NotReadyError,
    RateLimitedError,
    AllProvidersFailed,
)

def problem_details_response(
    status_code: int,
    code: str,
    title: str,
    detail: str,
    errors: list = None,
) -> JSONResponse:
    # Build standard RFC 7807 Problem Details response
    payload = {
        "type": f"https://scholarpilot.ai/errors/{code.lower()}",
        "title": title,
        "status": status_code,
        "code": code,
        "detail": detail,
        "errors": errors or [],
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )

async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    # Central exception mapper converting domain errors to Problem Details
    if isinstance(exc, NotFoundError):
        return problem_details_response(status.HTTP_404_NOT_FOUND, exc.code, "Not Found", exc.message)
    if isinstance(exc, MissingTokenError):
        return problem_details_response(status.HTTP_401_UNAUTHORIZED, exc.code, "Unauthorized", exc.message)
    if isinstance(exc, (ActiveJobExistsError, ConflictError, NotReadyError)):
        return problem_details_response(status.HTTP_409_CONFLICT, exc.code, "Conflict", exc.message)
    if isinstance(exc, RateLimitedError):
        return problem_details_response(status.HTTP_429_TOO_MANY_REQUESTS, exc.code, "Rate Limited", exc.message)
    if isinstance(exc, AllProvidersFailed):
        return problem_details_response(status.HTTP_503_SERVICE_UNAVAILABLE, exc.code, "Service Unavailable", exc.message)
    return problem_details_response(status.HTTP_400_BAD_REQUEST, exc.code, "Bad Request", exc.message)

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"loc": list(err.get("loc", [])), "msg": err.get("msg", ""), "type": err.get("type", "")} for err in exc.errors()]
    return problem_details_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        title="Validation Error",
        detail="The request body or parameters failed validation rules",
        errors=errors,
    )
