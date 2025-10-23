import os, requests, datetime as dt

def fetch_markets():
    """
    Returns a list of dicts with keys: title, url, platform, end_date
    Uses Polymarket's Gamma API: GET /markets
    """
    base = os.getenv("POLYMARKET_API_BASE","https://gamma-api.polymarket.com")
    url = f"{base}/markets"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = []
    for m in data:
        title = m.get("question") or m.get("title") or m.get("slug")
        if not title: 
            continue
        slug = m.get("slug") or ""
        # Event page path can be either /event/<slug> or /market/<id>; slug is preferable
        page_url = f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com/"
        end_date = m.get("endDate") or m.get("closeDate") or None
        results.append({
            "title": title.strip(),
            "url": page_url,
            "platform": "Polymarket",
            "end_date": end_date
        })
    return results
