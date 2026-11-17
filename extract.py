import json
import logging
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://api.artic.edu/api/v1/artworks"
API_FIELDS = (
    "id,title,artist_title,date_start,date_end,medium_display,"
    "place_of_origin,department_title,classification_title,image_id"
)
PAGE_SIZE = 100
REQUEST_DELAY = 1.0
TARGET_RECORDS = 3000
RAW_FILE = Path("data") / "raw_artworks.json"

log = logging.getLogger(__name__)
MAX_CONSECUTIVE_FAILS = 3
MAX_TOPUP_PAGES = 10
MAX_RETRY_AFTER = 60
HEADERS = {"User-Agent": "provenance-etl-student-project/1.0"}


def fetch_page(page, limit=PAGE_SIZE, retries=3):
    params = {"page": page, "limit": limit, "fields": API_FIELDS}
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)

            if r.status_code == 403:
                log.error("page %s: server answered 403 (blocked); not retrying", page)
                return None

            if r.status_code == 429:
                try:
                    wait = int(r.headers.get("Retry-After", 5 * attempt))
                except ValueError:
                    wait = 5 * attempt
                wait = min(wait, MAX_RETRY_AFTER)
                log.warning("page %s attempt %s/%s: rate limited (429), waiting %ss",
                            page, attempt, retries, wait)
                time.sleep(wait)
                continue

            r.raise_for_status()
            body = r.json()
            if "data" not in body or "pagination" not in body:
                raise ValueError("unexpected API response format (missing 'data' or 'pagination')")
            return body
        except (requests.RequestException, ValueError) as exc:
            log.warning("page %s attempt %s/%s failed: %s", page, attempt, retries, exc)
            time.sleep(2 * attempt)
    log.error("page %s skipped after %s failed attempts", page, retries)
    return None


def spread_pages(total_pages, n_pages):
    if n_pages >= total_pages:
        return list(range(1, total_pages + 1))
    if n_pages == 1:
        return [1]
    step = (total_pages - 1) / (n_pages - 1)
    return sorted({1 + round(i * step) for i in range(n_pages)})


def extract(target=TARGET_RECORDS, spread=True):
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)

    first = fetch_page(1)
    if first is None:
        raise RuntimeError("Could not reach the API (page 1 failed). Check your internet.")
    total_pages = first["pagination"]["total_pages"]
    n_pages = math.ceil(target / PAGE_SIZE)
    pages = spread_pages(total_pages, n_pages) if spread else list(range(1, n_pages + 1))
    log.info("API has %s pages; fetching %s pages: %s", total_pages, len(pages), pages)

    records, fetched = [], []
    fails = 0
    for p in pages:
        data = first if p == 1 else fetch_page(p)
        if data is not None:
            records.extend(data["data"])
            fetched.append(p)
            fails = 0
        else:
            fails += 1
            if fails >= MAX_CONSECUTIVE_FAILS:
                log.error("EXTRACT: %s pages in a row failed. The API is refusing us; stopping.", fails)
                break
        time.sleep(REQUEST_DELAY)

    if fails < MAX_CONSECUTIVE_FAILS:
        p, extra_tries = 2, 0
        while len(records) < target and p <= total_pages and extra_tries < MAX_TOPUP_PAGES:
            if p not in fetched:
                extra_tries += 1
                data = fetch_page(p)
                if data is not None:
                    records.extend(data["data"])
                    fetched.append(p)
                    fails = 0
                else:
                    fails += 1
                    if fails >= MAX_CONSECUTIVE_FAILS:
                        break
                time.sleep(REQUEST_DELAY)
            p += 1

    payload = {
        "source": API_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "page_size": PAGE_SIZE,
        "total_pages_in_api": total_pages,
        "pages": sorted(fetched),
        "count": len(records),
        "data": records,
    }
    if len(records) < target // 2:
        partial = RAW_FILE.with_name("raw_artworks_partial.json")
        partial.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        raise RuntimeError(
            f"Only {len(records)} of about {target} records could be fetched, so the saved raw file "
            f"was NOT changed (partial result kept in {partial.name}). The museum API may be "
            f"blocking or rate limiting you. Continue with your saved data using:  "
            f"python main.py --skip-extract")
    RAW_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("EXTRACT: saved %s records to %s", len(records), RAW_FILE)
    return records


def load_raw():
    return json.loads(RAW_FILE.read_text(encoding="utf-8"))["data"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else TARGET_RECORDS
    try:
        extract(target=target)
    except RuntimeError as exc:
        print("STOPPED:", exc)
