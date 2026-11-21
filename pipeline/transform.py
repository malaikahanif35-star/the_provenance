import json
import pandas as pd

RAW_FILE = "data/raw_artworks.json"
CLEAN_FILE = "data/clean_artworks.csv"

PLACE_FIXES = {
    "England": "United Kingdom",
    "Holland": "Netherlands",
}


def load_raw_df(path=RAW_FILE):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return pd.DataFrame(raw["data"])


def transform(df):
    df = df.copy()

    # 1. formating the text columns
    text_cols = ["title", "place_of_origin", "medium_display",
                 "department_title", "artist_title", "classification_title"]
    for col in text_cols:
        df[col] = df[col].str.strip()
        df[col] = df[col].replace("", pd.NA)

    # 2. changes the place names
    df["place_of_origin"] = df["place_of_origin"].replace(PLACE_FIXES)

    # 3. fill the empty spaces with unknown
    df["artist_title"] = df["artist_title"].fillna("Unknown Artist")
    for col in ["place_of_origin", "medium_display",
                "department_title", "classification_title"]:
        df[col] = df[col].fillna("Unknown")

    # 4. remove duplicates
    df = df.drop_duplicates(subset="id")

    # 5. Make whole numbers of the years
    df["date_start"] = df["date_start"].astype("Int64")
    df["date_end"] = df["date_end"].astype("Int64")

    # 6. Check the invalid rows
    bad = df[df["date_end"] < df["date_start"]]
    print("Invalid rows:", len(bad))

    # 7. New column
    df["year_span"] = df["date_end"] - df["date_start"]

    return df.reset_index(drop=True)


if __name__ == "__main__":
    df = load_raw_df()
    print("Complete data:", df.shape)

    clean = transform(df)
    print(clean.shape)
    print(clean.isnull().sum())
    print(clean["place_of_origin"].value_counts().head(15))

    clean.to_csv(CLEAN_FILE, index=False)