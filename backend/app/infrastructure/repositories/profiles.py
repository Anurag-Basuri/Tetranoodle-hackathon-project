import hashlib
import hmac
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import StudentProfileModel

def hash_token(token: str) -> str:
    # Compute SHA-256 hash of capability token
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

class ProfileRepository:
    # Database repository managing student profile storage and capability auth
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile_data: dict, access_token: str) -> StudentProfileModel:
        token_hash = hash_token(access_token)
        model = StudentProfileModel(
            data=profile_data,
            access_token_hash=token_hash,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_by_id(self, profile_id: str) -> Optional[StudentProfileModel]:
        stmt = select(StudentProfileModel).where(StudentProfileModel.id == profile_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def verify_token(self, profile_id: str, token: str) -> bool:
        # Securely compare token hash using constant time comparison
        profile = await self.get_by_id(profile_id)
        if not profile:
            return False
        provided_hash = hash_token(token)
        return hmac.compare_digest(profile.access_token_hash, provided_hash)

    async def update(self, profile_id: str, profile_data: dict) -> Optional[StudentProfileModel]:
        profile = await self.get_by_id(profile_id)
        if not profile:
            return None
        profile.data = profile_data
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
