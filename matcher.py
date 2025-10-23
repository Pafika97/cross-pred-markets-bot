import re
from rapidfuzz import fuzz, process

STOPWORDS = set("""a an the is are was were will would shall should of for with in on at to from by and or not be as if when where which who whom what how do does did has have had it's its
will? rate? rates? election elections president presidential us usa united states fed fomc""".split())

def normalize_title(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9%$€£&/@+\-\s]", " ", s)
    tokens = [t for t in s.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)

def match_cross_platform(markets, threshold=86, require_at_least=2):
    """
    markets: list of dicts with keys: title, url, platform, end_date
    returns: list of clusters, each is a list of market dicts that are similar
    """
    # Group by normalized titles using fuzzy token set ratio across platforms
    items = [(i, normalize_title(m['title']), m) for i, m in enumerate(markets)]
    used = set()
    clusters = []
    for i, norm_i, m_i in items:
        if i in used:
            continue
        cluster = [m_i]
        used.add(i)
        for j, norm_j, m_j in items:
            if j in used or j == i:
                continue
            score = fuzz.token_set_ratio(norm_i, norm_j)
            if score >= threshold and m_j['platform'] != m_i['platform']:
                cluster.append(m_j)
                used.add(j)
        # ensure multi-platform
        if len({x['platform'] for x in cluster}) >= require_at_least:
            clusters.append(cluster)
    return clusters
