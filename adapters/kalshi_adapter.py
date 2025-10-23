import os, requests

def fetch_markets():
    """
    Returns a list of dicts with keys: title, url, platform, end_date
    Uses Kalshi's public API (no auth needed):
    GET {base}/markets?limit=1000
    Docs: https://docs.kalshi.com/getting_started/quick_start_market_data
    """
    base = os.getenv("KALSHI_API_BASE","https://api.elections.kalshi.com/trade-api/v2")
    limit = int(os.getenv("KALSHI_LIMIT","1000"))
    url = f"{base}/markets?limit={limit}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    markets = data.get("markets") or []
    results = []
    for m in markets:
        title = m.get("title") or m.get("name") or m.get("ticker") or ""
        if not title:
            continue
        # compose a nice URL to the market page if available
        ticker = m.get("ticker") or ""
        page_url = f"https://kalshi.com/markets/{ticker}" if ticker else "https://kalshi.com/markets"
        end_date = m.get("close_time") or m.get("settlement_time") or None
        results.append({
            "title": title.strip(),
            "url": page_url,
            "platform": "Kalshi",
            "end_date": end_date
        })
    return results
