import secrets
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import get_db
from app.infrastructure.repositories.profiles import ProfileRepository
from app.api.deps import get_current_profile
from app.infrastructure.models import StudentProfileModel
from app.api.schemas import ProfileCreate, ProfileCreateResponse, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProfileCreateResponse)
async def create_profile(
    payload: ProfileCreate,
    db: AsyncSession = Depends(get_db),
):
    # Register new student profile and issue capability token
    token = secrets.token_urlsafe(32)
    repo = ProfileRepository(db)
    model = await repo.create(payload.model_dump(mode="json"), token)
    return ProfileCreateResponse(
        id=model.id,
        access_token=token,
        profile=model.data,
    )

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_profile: StudentProfileModel = Depends(get_current_profile),
):
    # Retrieve student profile for authorized token holder
    return ProfileResponse(
        id=current_profile.id,
        profile=current_profile.data,
        created_at=current_profile.created_at,
        updated_at=current_profile.updated_at,
    )

@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    payload: ProfileCreate,
    current_profile: StudentProfileModel = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    # Update profile fields
    repo = ProfileRepository(db)
    updated = await repo.update(profile_id, payload.model_dump(mode="json"))
    return ProfileResponse(
        id=updated.id,
        profile=updated.data,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )
