from typing import Tuple
from app.tools.extractors import extract_pdf_text

def extract_uploaded_document(
    content: bytes,
    filename: str,
    mime_type: str = "",
) -> Tuple[str, str]:
    # Extract readable text from uploaded resume or transcript bytes
    if not content:
        return "", "failed: empty file"

    name_lower = filename.lower()
    mime_lower = mime_type.lower()

    if name_lower.endswith(".pdf") or "pdf" in mime_lower:
        text = extract_pdf_text(content)
        if text:
            return text, "completed"
        return "", "failed: could not extract text from PDF"

    # Plain text or markdown
    try:
        decoded = content.decode("utf-8", errors="replace").strip()
        if decoded:
            return decoded, "completed"
        return "", "failed: empty text content"
    except Exception as e:
        return "", f"failed: {e}"
