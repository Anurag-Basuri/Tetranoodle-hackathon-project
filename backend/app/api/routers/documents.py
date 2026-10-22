import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db import get_db
from app.api.deps import get_current_profile
from app.infrastructure.models import StudentProfileModel, StudentDocumentModel
from app.api.schemas import DocumentOut
from app.tools.documents import extract_uploaded_document

router = APIRouter(prefix="/profiles/{profile_id}/documents", tags=["Documents"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=DocumentOut)
async def upload_document(
    profile_id: str,
    file: UploadFile = File(...),
    kind: str = Form("resume"),
    current_profile: StudentProfileModel = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    # Ingest resume or transcript document
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed 5 MB limit",
        )

    # Extract text from PDF or raw document
    extracted_text, extract_status = extract_uploaded_document(
        content,
        file.filename or "document.txt",
        file.content_type or "",
    )

    doc_model = StudentDocumentModel(
        id=str(uuid.uuid4()),
        profile_id=profile_id,
        kind=kind,
        filename=file.filename or "document",
        mime=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
        extracted_text=extracted_text,
        extraction_status=extract_status,
    )
    db.add(doc_model)
    await db.commit()
    await db.refresh(doc_model)

    return DocumentOut(
        id=doc_model.id,
        profile_id=doc_model.profile_id,
        kind=doc_model.kind,
        filename=doc_model.filename,
        size_bytes=doc_model.size_bytes,
        extraction_status=doc_model.extraction_status,
        created_at=doc_model.created_at,
    )

@router.get("", response_model=List[DocumentOut])
async def list_documents(
    profile_id: str,
    current_profile: StudentProfileModel = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    # List all uploaded documents for this student
    stmt = select(StudentDocumentModel).where(StudentDocumentModel.profile_id == profile_id)
    res = await db.execute(stmt)
    docs = res.scalars().all()

    return [
        DocumentOut(
            id=d.id,
            profile_id=d.profile_id,
            kind=d.kind,
            filename=d.filename,
            size_bytes=d.size_bytes,
            extraction_status=d.extraction_status,
            created_at=d.created_at,
        )
        for d in docs
    ]
