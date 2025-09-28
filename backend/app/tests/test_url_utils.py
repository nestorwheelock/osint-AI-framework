from app.utils.url import canonicalize_url

def test_canonicalize_url_variants():
    a = "https://example.com/post?id=123&utm_source=x#frag"
    b = "https://EXAMPLE.com/post?utm_medium=y&id=123"
    assert canonicalize_url(a) == canonicalize_url(b)
