from app.tools.github import extract_github_username

def test_extract_github_username_formats():
    # Test different user profile URL styles
    assert extract_github_username("https://github.com/rahul-sharma") == "rahul-sharma"
    assert extract_github_username("https://github.com/rahul-sharma/") == "rahul-sharma"
    assert extract_github_username("http://github.com/student123/repo") == "student123"
    assert extract_github_username("johndoe") == "johndoe"
    assert extract_github_username("") is None
