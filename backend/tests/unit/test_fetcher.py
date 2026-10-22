from app.tools.fetcher import validate_ssrf_safety

def test_ssrf_blocks_localhost():
    # SSRF guard must reject loopback addresses
    is_safe, error = validate_ssrf_safety("http://localhost/secret")
    assert is_safe is False

    is_safe, error = validate_ssrf_safety("http://127.0.0.1:8000/admin")
    assert is_safe is False

def test_ssrf_blocks_private_subnets():
    # SSRF guard must reject private network addresses
    is_safe, error = validate_ssrf_safety("http://192.168.1.1/router")
    assert is_safe is False

    is_safe, error = validate_ssrf_safety("http://10.0.0.5/internal")
    assert is_safe is False

def test_ssrf_blocks_aws_metadata():
    # SSRF guard must reject cloud metadata endpoint
    is_safe, error = validate_ssrf_safety("http://169.254.169.254/latest/meta-data/")
    assert is_safe is False

def test_ssrf_allows_public_web():
    # SSRF guard allows benign public domain
    is_safe, error = validate_ssrf_safety("https://www.google.com")
    assert is_safe is True
