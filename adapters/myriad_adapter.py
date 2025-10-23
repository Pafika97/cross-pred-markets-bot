import os, requests

def fetch_markets():
    """
    Returns a list of dicts with keys: title, url, platform, end_date
    Myriad partner REST API likely requires an API key. If MYRIAD_API_KEY is not set,
    this adapter returns an empty list (graceful disable).
    Docs example: https://partner-docs.myriad.com/apis/rest (subject to updates).
    """
    base = os.getenv("MYRIAD_API_BASE","").strip()
    api_key = os.getenv("MYRIAD_API_KEY","").strip()
    if not base or not api_key:
        # Disabled if not configured
        return []
    headers = {"Authorization": f"Bearer {api_key}"}
    # NOTE: Replace the path below with the correct partner endpoint for market discovery.
    url = f"{base.rstrip('/')}/markets"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    # normalize assuming a list of objects
    results = []
    for m in data:
        title = m.get("title") or m.get("question") or m.get("name")
        if not title:
            continue
        page_url = m.get("url") or "https://myriad.markets/"
        end_date = m.get("endDate") or m.get("close_time") or None
        results.append({
            "title": title.strip(),
            "url": page_url,
            "platform": "Myriad",
            "end_date": end_date
        })
    return results
