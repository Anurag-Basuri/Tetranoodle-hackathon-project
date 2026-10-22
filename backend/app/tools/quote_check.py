import re
from rapidfuzz import fuzz

def normalize_text(text: str) -> str:
    # Lowercase, replace smart quotes/dashes, and collapse spaces
    if not text:
        return ""
    cleaned = text.lower()
    cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("’", "'").replace("‘", "'")
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

def verify_excerpt(excerpt: str, page_text: str, min_ratio: float = 92.0) -> tuple[bool, str]:
    # Check if extracted excerpt exists verbatim or near verbatim in page
    if not excerpt or not page_text:
        return False, excerpt

    norm_excerpt = normalize_text(excerpt)
    norm_page = normalize_text(page_text)

    # Fast path: exact substring match
    if norm_excerpt in norm_page:
        return True, excerpt

    # Fuzzy path using partial ratio for slight OCR/formatting differences
    ratio = fuzz.partial_ratio(norm_excerpt, norm_page)
    if ratio >= min_ratio:
        return True, excerpt

    # If match ratio is too low, reject to prevent LLM hallucinations
    return False, excerpt
