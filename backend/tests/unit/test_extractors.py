from app.domain.enums import SourceType
from app.tools.extractors import classify_source_url, extract_html_text

def test_classify_aggregator():
    # Known aggregator domains must be classified as aggregator
    assert classify_source_url("https://www.scholars4dev.com/masters") == SourceType.AGGREGATOR
    assert classify_source_url("https://shiksha.com/studyabroad") == SourceType.AGGREGATOR
    assert classify_source_url("https://studyportals.com/scholarships") == SourceType.AGGREGATOR

def test_classify_official():
    # University and government domains must be classified as official
    assert classify_source_url("https://www.daad.de/en/find-funding/") == SourceType.OFFICIAL
    assert classify_source_url("https://cs.stanford.edu/admissions") == SourceType.OFFICIAL
    assert classify_source_url("https://www.ox.ac.uk/graduate") == SourceType.OFFICIAL
    assert classify_source_url("https://www.tu-berlin.de/programs") == SourceType.OFFICIAL

def test_classify_unknown():
    # Personal blogs or uncategorized platforms are marked unknown
    assert classify_source_url("https://medium.com/@student/my-scholarship-tips") == SourceType.UNKNOWN

def test_extract_html_text():
    html = "<html><head><title>Test</title></head><body><script>console.log('remove');</script><h1>Scholarship Requirements</h1><p>Applicants must hold an undergraduate degree in engineering.</p></body></html>"
    text = extract_html_text(html)
    assert "undergraduate degree" in text
    assert "console.log" not in text
