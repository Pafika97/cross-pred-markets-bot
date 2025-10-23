import os, time, csv
from dotenv import load_dotenv
from adapters.polymarket_adapter import fetch_markets as pm_fetch
from adapters.kalshi_adapter import fetch_markets as ks_fetch
from adapters.myriad_adapter import fetch_markets as my_fetch
from matcher import match_cross_platform
from notifier import send_telegram_message

def get_env_int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

def run_once():
    all_markets = []
    for fetch, label in [(pm_fetch, "Polymarket"), (ks_fetch, "Kalshi"), (my_fetch, "Myriad")]:
        try:
            data = fetch()
            print(f"[INFO] fetched {len(data)} from {label}")
            all_markets.extend(data)
        except Exception as e:
            print(f"[ERROR] fetching {label}: {e}")

    title_threshold = get_env_int("TITLE_SIM_THRESHOLD", 86)
    require_at_least = get_env_int("REQUIRE_AT_LEAST", 2)
    clusters = match_cross_platform(all_markets, threshold=title_threshold, require_at_least=require_at_least)

    if not clusters:
        print("[INFO] No cross-platform matches found this run.")
        return

    # Optional logging
    log_path = os.getenv("MATCH_LOG_PATH","").strip()
    if log_path:
        header = ["platforms","titles","urls"]
        write_header = not os.path.exists(log_path)
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header: w.writerow(header)
            for cluster in clusters:
                w.writerow([
                    " | ".join(sorted({c['platform'] for c in cluster})),
                    " | ".join([c['title'] for c in cluster]),
                    " | ".join([c['url'] for c in cluster]),
                ])

    # Compose Telegram message(s)
    for cluster in clusters:
        lines = []
        platforms = sorted({c['platform'] for c in cluster})
        lines.append(f"<b>Совпадение темы на нескольких платформах</b> — {', '.join(platforms)}")
        for c in cluster:
            lines.append(f"• <b>{c['platform']}</b>: {c['title']}")
            lines.append(f"  {c['url']}")
        text = "\n".join(lines)
        send_telegram_message(text)

def main():
    load_dotenv()
    poll = get_env_int("POLL_SECONDS", 300)
    print(f"[START] Cross-platform watcher (every {poll}s). Press Ctrl+C to stop.")
    while True:
        try:
            run_once()
        except Exception as e:
            print("[FATAL] run_once:", e)
        time.sleep(poll)

if __name__ == "__main__":
    main()
