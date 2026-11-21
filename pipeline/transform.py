import re

import pandas as pd

CLEAN_FILE = "data/clean_artworks.csv"

KEEP_COLS = [
    "id", "title", "date_start", "date_end", "place_of_origin",
    "medium_display", "department_title", "artist_title",
    "classification_title", "image_id",
]

TEXT_COLS = [
    "title", "artist_title", "medium_display",
    "department_title", "classification_title",
]

COUNTRY_FIX = {
    "England": "United Kingdom",
    "Holland": "Netherlands",
}


def strip_html(text):
    """<em>Linga</em> jaise HTML tags hata deta hai."""
    if isinstance(text, str):
        return re.sub(r"<[^>]+>", "", text).strip()
    return text


def transform(df):
    df = df.copy()

    # Sirf zaroori columns rakho
    df = df[[c for c in KEEP_COLS if c in df.columns]]

    # Duplicate artworks hatao
    df = df.drop_duplicates(subset="id")

    # Invalid rows (id ya title missing) hatao
    before = len(df)
    df = df.dropna(subset=["id", "title"])
    print("Invalid rows:", before - len(df))

    # HTML tags saaf karo
    for col in TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].apply(strip_html)

    # Countries ke naam theek karo
    df["place_of_origin"] = df["place_of_origin"].replace(COUNTRY_FIX)

    # Missing text ko Unknown se bharo (dates aur image_id null rehte hain)
    df["artist_title"] = df["artist_title"].fillna("Unknown Artist")
    for col in ["place_of_origin", "medium_display",
                "department_title", "classification_title"]:
        df[col] = df[col].fillna("Unknown")

    # Dates ko numbers banao aur year_span nikalo
    df["date_start"] = pd.to_numeric(df["date_start"], errors="coerce")
    df["date_end"] = pd.to_numeric(df["date_end"], errors="coerce")
    df["year_span"] = df["date_end"] - df["date_start"]

    df = df.reset_index(drop=True)
    df.to_csv(CLEAN_FILE, index=False)
    return df


if __name__ == "__main__":
    import json

    with open("data/raw_artworks.json", encoding="utf-8") as f:
        raw_df = pd.DataFrame(json.load(f)["data"])
    out = transform(raw_df)
    print("Rows:", len(out))