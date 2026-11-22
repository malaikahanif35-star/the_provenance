import json
import os
import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DB_FILE = "data/artworks.db"
RAW_FILE = "data/raw_artworks.json"
REJECTED_FILE = "data/rejected/rejected_artworks.json"
CHART_DIR = "data/charts"
REPORT_FILE = "data/eda_report.txt"

CENTURY_SQL = """
SELECT (date_start - 1) / 100 + 1 AS century, COUNT(*) AS n
FROM artworks
WHERE date_start > 0
GROUP BY century
ORDER BY century
"""

MEDIUM_SQL = """
SELECT substr(medium_display, 1, 40) AS label, COUNT(*) AS n
FROM artworks
WHERE medium_display != 'Unknown'
GROUP BY label
ORDER BY n DESC
LIMIT 10
"""

PLACE_SQL = """
SELECT place_of_origin AS label, COUNT(*) AS n
FROM artworks
WHERE place_of_origin != 'Unknown'
GROUP BY place_of_origin
ORDER BY n DESC
LIMIT 10
"""

DEPARTMENT_SQL = """
SELECT department_title AS label, COUNT(*) AS n
FROM artworks
GROUP BY department_title
ORDER BY n DESC
"""

ARTIST_SQL = """
SELECT CASE WHEN artist_title IN ('Unknown Artist', 'Unknown') THEN 'Unknown' ELSE 'Known' END AS label,
       COUNT(*) AS n
FROM artworks
GROUP BY label
"""


def save_bar(data, x, y, title, filename):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=data, x=x, y=y)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename))
    plt.close()


def read_json_count(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data["data"]
    return len(data)


def run_eda(db_file=DB_FILE):
    os.makedirs(CHART_DIR, exist_ok=True)
    sns.set_theme(style="whitegrid")

    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM artworks", conn)
    centuries = pd.read_sql_query(CENTURY_SQL, conn)
    mediums = pd.read_sql_query(MEDIUM_SQL, conn)
    places = pd.read_sql_query(PLACE_SQL, conn)
    departments = pd.read_sql_query(DEPARTMENT_SQL, conn)
    artists = pd.read_sql_query(ARTIST_SQL, conn)
    conn.close()

    total = len(df)
    if total == 0:
        print("EDA: the artworks table is empty, nothing to analyse.")
        return

    extracted = read_json_count(RAW_FILE)
    rejected = read_json_count(REJECTED_FILE)
    stats = pd.DataFrame({
        "stage": ["Extracted", "Rejected", "Loaded"],
        "rows": [extracted, rejected, total],
    })

    missing = []
    for col in df.columns:
        count = int(df[col].isna().sum() + df[col].isin(["Unknown", "Unknown Artist"]).sum())
        missing.append({"column": col, "missing": count, "percent": round(count / total * 100, 1)})
    missing = pd.DataFrame(missing).sort_values("missing", ascending=False)

    summary = df[["date_start", "date_end", "year_span"]].describe().round(1)

    plt.figure(figsize=(10, 6))
    sns.histplot(df["date_start"].dropna(), bins=50)
    plt.title("Distribution of start years")
    plt.xlabel("Year (negative = BCE)")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "year_distribution.png"))
    plt.close()

    save_bar(missing, "percent", "column", "Missing or unknown values (%)", "missing_values.png")
    save_bar(centuries, "century", "n", "Artworks per century", "artworks_per_century.png")
    save_bar(mediums, "n", "label", "Top 10 mediums", "top_mediums.png")
    save_bar(places, "n", "label", "Top 10 places of origin", "top_places.png")
    save_bar(departments, "n", "label", "Artworks per department", "departments.png")
    save_bar(artists, "label", "n", "Known vs unknown artists", "unknown_artists.png")
    save_bar(stats, "rows", "stage", "Pipeline statistics", "pipeline_stats.png")

    top_century = centuries.loc[centuries["n"].idxmax()]
    century = int(top_century["century"])
    top_department = departments.iloc[0]
    top_medium = mediums.iloc[0]
    top_place = places.iloc[0]
    unknown_artists = int(artists.loc[artists["label"] == "Unknown", "n"].sum())
    no_year = int(df["date_start"].isna().sum())
    before_year_1 = int((df["date_start"] <= 0).sum())

    insights = [
        f"Century {century} (years {(century - 1) * 100 + 1} to {century * 100}) has the most "
        f"artworks: {int(top_century['n'])}.",
        f"The largest department is {top_department['label']} with {int(top_department['n'])} "
        f"artworks ({top_department['n'] / total * 100:.1f}% of the data).",
        f"The most used medium is '{top_medium['label']}' ({int(top_medium['n'])} artworks).",
        f"The most common place of origin is {top_place['label']} ({int(top_place['n'])} artworks).",
        f"{unknown_artists / total * 100:.1f}% of the artworks have an unknown artist.",
        f"{no_year / total * 100:.1f}% of the artworks have no year, so they are left out of the "
        f"year and century charts.",
    ]

    lines = ["EDA REPORT", "=" * 40, ""]
    lines.append("PIPELINE STATS")
    lines.append(f"Rows extracted: {extracted}")
    lines.append(f"Rows rejected:  {rejected}")
    lines.append(f"Rows loaded:    {total}")
    lines.append(f"Removed in transform (duplicates / invalid): {extracted - rejected - total}")
    lines.append("")
    lines.append("SUMMARY STATISTICS")
    lines.append(summary.to_string())
    lines.append("")
    lines.append("MISSING / UNKNOWN VALUES")
    lines.append(missing.to_string(index=False))
    lines.append("")
    lines.append(f"Artworks before year 1 (not in the century chart): {before_year_1}")
    lines.append("")
    lines.append("INSIGHTS")
    for number, text in enumerate(insights, start=1):
        lines.append(f"{number}. {text}")

    report = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print("Charts saved in:", CHART_DIR)
    print("Report saved:", REPORT_FILE)


if __name__ == "__main__":
    run_eda()