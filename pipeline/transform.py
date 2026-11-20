import json
import pandas as pd

RAW_FILE = "data/raw/artworks_raw.json"


def ordinal(n):
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 11 -> 11th, 21 -> 21st"""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def get_century(year):
    """Saal se century ka naam banata hai. Maloom na ho to 'Unknown'."""
    if pd.isna(year):
        return "Unknown"
    year = int(year)
    if year > 0:
        return f"{ordinal((year - 1) // 100 + 1)} century"
    return f"{ordinal((abs(year) - 1) // 100 + 1)} century BCE"


def transform(raw_file=RAW_FILE):
    # 1. JSON file parho aur table banao
    with open(raw_file, encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    print("Raw rows:", len(df))

    # 2. Column ke naam team ke naamon ke mutabiq karo
    df = df.rename(columns={
        "artist_title": "artist",
        "medium_display": "medium",
        "department_title": "department",
        "classification_title": "classification",
    })

    # 3. Duplicates hatao (sirf id se)
    before = len(df)
    df = df.drop_duplicates(subset="id")
    print("Duplicates removed:", before - len(df))

    # 4. Text columns se extra spaces hatao
    text_columns = ["title", "artist", "medium", "place_of_origin",
                    "department", "classification"]
    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    # 5. Khali artist aur place ko "Unknown" karo
    df["artist"] = df["artist"].fillna("Unknown")
    df["place_of_origin"] = df["place_of_origin"].fillna("Unknown")

    # 6. Naye columns
    df["century"] = df["date_start"].apply(get_century)
    df["has_image"] = df["image_id"].notna()

    print("Rows after transform:", len(df))
    return df


if __name__ == "__main__":
    df = transform()
    print(df.head())
    print(df.isna().sum())
    print(df["century"].value_counts())