from app.tools.quote_check import verify_excerpt, normalize_text

def test_normalize_text():
    raw = "Applicants   MUST have “Grade 8.0”—minimum."
    norm = normalize_text(raw)
    assert norm == "applicants must have \"grade 8.0\"-minimum."

def test_verify_excerpt_exact():
    page = "Eligibility: Applicants must hold a Bachelor of Science degree in Computer Science."
    excerpt = "Applicants must hold a Bachelor of Science degree in Computer Science."
    verified, matched = verify_excerpt(excerpt, page)
    assert verified is True

def test_verify_excerpt_fuzzy():
    # Minor typographical variations should still pass
    page = "International candidates must have at least 7.5 on the IELTS academic exam."
    excerpt = "International candidates must have at least 7.5 on the IELTS Academic exam."
    verified, matched = verify_excerpt(excerpt, page)
    assert verified is True

def test_verify_excerpt_hallucinated():
    # Hallucinated requirement absent from the page must fail
    page = "TU Munich offers merit grants for international engineering students."
    excerpt = "100% full funding of 50,000 EUR per semester guaranteed."
    verified, matched = verify_excerpt(excerpt, page)
    assert verified is False
