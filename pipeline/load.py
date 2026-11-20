import json
import sqlite3

DB_FILE = "data/artworks.db"
JSON_FILE = "data/artworks_clean.json"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS artworks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT,
    date_start INTEGER,
    date_end INTEGER,
    medium TEXT,
    place_of_origin TEXT,
    department TEXT,
    classification TEXT,
    image_id TEXT,
    century TEXT,
    has_image INTEGER
)
"""


def load(good_df):
    df = good_df.copy()
    # SQLite mein None/NaN sahi se jaye, aur True/False 1/0 ban jaye
    df["has_image"] = df["has_image"].astype(int)
    df = df.astype(object).where(df.notna(), None)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("DROP TABLE IF EXISTS artworks")  # har run par naya, duplicate nahi
    conn.execute(CREATE_TABLE)

    columns = ["id", "title", "artist", "date_start", "date_end", "medium",
               "place_of_origin", "department", "classification",
               "image_id", "century", "has_image"]
    placeholders = ", ".join("?" for _ in columns)
    rows = [tuple(r[c] for c in columns) for r in df.to_dict(orient="records")]

    conn.executemany(
        f"INSERT INTO artworks ({', '.join(columns)}) VALUES ({placeholders})",
        rows,
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM artworks").fetchone()[0]
    conn.close()
    print("Rows loaded into database:", count)

    # Website ke liye JSON export
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(rows_to_dicts(rows, columns), f, ensure_ascii=False, indent=2)
    print("Exported JSON:", JSON_FILE)
    return count


def rows_to_dicts(rows, columns):
    return [dict(zip(columns, r)) for r in rows]


if __name__ == "__main__":
    from pipeline.transform import transform
    from pipeline.validate import validate

    df = transform()
    good_df, rejected = validate(df)
    load(good_df)