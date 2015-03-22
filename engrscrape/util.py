from xxhash import xxh64
from urlparse import urljoin, urlsplit

# Hash the url. Can change hash function if necessary, but xxhash is fast.
def gethash(url):
    return xxh64(url).hexdigest()

# Filter out any domains that are not a part of the domain(s) we care about
def in_domains(url, allow_domains):
    return any(ad in urlsplit(url).netloc for ad in allow_domains)

# Fix link to not include any weird spaces and stuff
def fix_link(link, baseurl):
    s = urlsplit(link.strip().strip('.').rstrip('/'))
    if s.scheme:
        return urljoin(baseurl, s.scheme + '://' + s.netloc + s.path)
    else:
        return urljoin(baseurl, s.path)
