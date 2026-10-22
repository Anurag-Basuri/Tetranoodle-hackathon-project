from typing import Optional
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import get_db
from app.infrastructure.repositories.profiles import ProfileRepository
from app.infrastructure.models import StudentProfileModel

async def get_current_profile(
    profile_id: str,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileModel:
    # Authenticate student access via capability token
    if not x_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-Access-Token header",
        )

    repo = ProfileRepository(db)
    is_valid = await repo.verify_token(profile_id, x_access_token)
    if not is_valid:
        # Return 404 on token mismatch per security specification
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found or access denied",
        )

    profile = await repo.get_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile
