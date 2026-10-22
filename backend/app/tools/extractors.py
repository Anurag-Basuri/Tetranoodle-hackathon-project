import io
import re
from urllib.parse import urlparse
import trafilatura
from pypdf import PdfReader
from app.domain.enums import SourceType

# Known aggregator websites that must not be used as official proof
AGGREGATOR_DENYLIST = {
    "scholars4dev.com",
    "shiksha.com",
    "studyportals.com",
    "leverageedu.com",
    "collegedunia.com",
    "wemakescholars.com",
    "hotcoursesabroad.com",
    "daadscholarship.com",
    "findaphd.com",
    "mastersportal.com",
}

# Recognized official domains and awarding bodies
OFFICIAL_ALLOWLIST = {
    "daad.de",
    "chevening.org",
    "fulbrightprogram.org",
    "erasmus-plus.ec.europa.eu",
    "campusfrance.org",
    "singaporeedu.gov.sg",
    "tum.de",
    "lmu.de",
    "rwth-aachen.de",
    "uwaterloo.ca",
    "utoronto.ca",
    "ubc.ca",
    "nus.edu.sg",
    "ntu.edu.sg",
}

def classify_source_url(url: str) -> SourceType:
    # Classify whether URL is official institution or aggregator
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except Exception:
        return SourceType.UNKNOWN

    if not host:
        return SourceType.UNKNOWN

    # Check aggregator denylist first
    for denied in AGGREGATOR_DENYLIST:
        if host == denied or host.endswith("." + denied):
            return SourceType.AGGREGATOR

    # Check official allowlist
    for allowed in OFFICIAL_ALLOWLIST:
        if host == allowed or host.endswith("." + allowed):
            return SourceType.OFFICIAL

    # Regex patterns for academic and government domains
    patterns = [
        r"\.edu(\.[a-z]{2})?$",
        r"\.ac\.[a-z]{2,}$",
        r"\.gov(\.[a-z]{2})?$",
        r"(\.|^)(tu|uni)-[a-z0-9-]+\.de$",
    ]
    for pat in patterns:
        if re.search(pat, host):
            return SourceType.OFFICIAL

    return SourceType.UNKNOWN

def extract_html_text(html_content: str) -> str:
    # Extract clean readable article text from raw HTML using trafilatura
    if not html_content:
        return ""

    try:
        extracted = trafilatura.extract(
            html_content,
            include_links=False,
            include_images=False,
            include_tables=True,
            output_format="txt",
        )
        if extracted and len(extracted.strip()) > 50:
            return extracted.strip()
    except Exception:
        pass

    # Simple regex fallback if trafilatura extraction returns empty
    cleaned = re.sub(r"<script[^>]*>.*?</script>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<style[^>]*>.*?</style>", " ", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def extract_pdf_text(pdf_bytes: bytes) -> str:
    # Extract text from PDF bytes with pypdf and fallback to pdfplumber
    if not pdf_bytes:
        return ""

    text_parts = []
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        if text_parts:
            return "\n\n".join(text_parts).strip()
    except Exception:
        pass

    # Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            if text_parts:
                return "\n\n".join(text_parts).strip()
    except Exception:
        pass

    return ""
