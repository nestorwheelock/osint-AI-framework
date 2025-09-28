from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode

_DROP_PARAMS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"}

def canonicalize_url(url: str) -> str:
    p = urlparse(url)
    host = p.netloc.lower()
    path = p.path or "/"
    q = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if k not in _DROP_PARAMS]
    q.sort()
    new = (p.scheme.lower() or "https", host, path, "", urlencode(q), "")
    return urlunparse(new)
