import json
import time
import requests

API_URL = "https://api.artic.edu/api/v1/artworks"
FIELDS = "id,title,artist_title,date_start,date_end,medium_display,place_of_origin,department_title,classification_title,image_id"
HEADERS = {"User-Agent": "TheProvenanceStudentProject/1.0 (student ETL project)"}
RAW_FILE = "data/raw/artworks_raw.json"


def fetch_page(page, limit=100):
    """Ek page laata hai. Fail ho to 3 baar dobara koshish karta hai."""
    params = {"page": page, "limit": limit, "fields": FIELDS}
    for attempt in range(1, 4):
        try:
            response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()["data"]
        except requests.RequestException as error:
            print(f"Page {page}, koshish {attempt} fail: {error}")
            time.sleep(3)
    return None


def extract(total_pages=30):
    """total_pages x 100 = records. 30 pages = 3,000 records."""
    all_records = []
    for page in range(1, total_pages + 1):
        data = fetch_page(page)
        if data is None:
            print(f"Page {page} skip kar diya.")
            continue
        all_records.extend(data)
        print(f"Page {page}/{total_pages} done. Total records: {len(all_records)}")
        time.sleep(1)

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_records)} records to {RAW_FILE}")
    return all_records


if __name__ == "__main__":
    extract(total_pages=30)