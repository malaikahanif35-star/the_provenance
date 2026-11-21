import sqlite3
import pandas as pd

COLUMNS = ["id", "title", "artist_title", "date_start", "date_end",
           "medium_display", "place_of_origin", "department_title",
           "classification_title", "image_id", "has_image", "year_span"]


def load(df, db_path="data/artworks.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS artworks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        artist_title TEXT,
        date_start INTEGER,
        date_end INTEGER,
        medium_display TEXT,
        place_of_origin TEXT,
        department_title TEXT,
        classification_title TEXT,
        image_id TEXT,
        has_image INTEGER,
        year_span INTEGER
    )
    """)

    df = df[COLUMNS]

    for _, row in df.iterrows():
        values = []
        for v in row:
            if pd.isna(v):
                values.append(None)
            else:
                values.append(v)
        cur.execute(
            "INSERT OR REPLACE INTO artworks VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            values,
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM artworks")
    count = cur.fetchone()[0]
    print("Rows sent:", len(df))
    print("Rows in database:", count)

    conn.close()
    return count


if __name__ == "__main__":
    df = pd.read_csv("data/validated_artworks.csv")
    load(df)