import json
import os
from typing import Optional

import pandas as pd
from pydantic import BaseModel, field_validator, model_validator

MIN_YEAR = -5000
MAX_YEAR = 2026
RAW_FILE = "data/raw_artworks.json"
REJECTED_FILE = "data/rejected/rejected_artworks.json"
REPORT_FILE = "data/quality_report.txt"


class Artwork(BaseModel):
    id: int
    title: str
    artist: str = "Unknown"
    date_start: Optional[int] = None
    date_end: Optional[int] = None
    medium: Optional[str] = None
    place_of_origin: str = "Unknown"
    department: Optional[str] = None
    classification: Optional[str] = None
    image_id: Optional[str] = None
    century: str = "Unknown"
    has_image: bool = False

    @field_validator("id")
    @classmethod
    def id_positive(cls, v):
        if v <= 0:
            raise ValueError("id must be positive")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("title is empty")
        return v

    @field_validator("date_start", "date_end")
    @classmethod
    def year_in_range(cls, v):
        if v is not None and not (MIN_YEAR <= v <= MAX_YEAR):
            raise ValueError(f"year {v} outside {MIN_YEAR}..{MAX_YEAR}")
        return v

    @model_validator(mode="after")
    def end_not_before_start(self):
        if (self.date_start is not None and self.date_end is not None
                and self.date_end < self.date_start):
            raise ValueError("date_end is before date_start")
        return self


def clean_row(row):
    """pandas ki NaN/NA values ko None banata hai, taake Pydantic samjhe."""
    cleaned = {}
    for key, value in row.items():
        if pd.isna(value):
            cleaned[key] = None
        elif key in ("date_start", "date_end"):
            cleaned[key] = int(value)
        else:
            cleaned[key] = value
    for key in ("artist", "place_of_origin", "century"):
        if cleaned.get(key) is None:
            cleaned.pop(key, None)
    return cleaned


def write_quality_report(df, good_df, rejected):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

    lines = []
    lines.append("DATA QUALITY REPORT")
    lines.append("=" * 40)
    lines.append(f"Rows received:   {len(df)}")
    lines.append(f"Rows passed:     {len(good_df)}")
    lines.append(f"Rows rejected:   {len(rejected)}")
    lines.append("")
    lines.append("Rejection reasons:")
    if rejected:
        for r in rejected:
            lines.append(f"  id {r['id']}: {r['reject_reason']}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Missing values in received data:")
    for col, n in df.isna().sum().items():
        lines.append(f"  {col}: {n}")
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Quality report saved:", REPORT_FILE)


def validate(df):
    os.makedirs(os.path.dirname(REJECTED_FILE), exist_ok=True)

    good_rows = []
    rejected = []

    for row in df.to_dict(orient="records"):
        data = clean_row(row)
        try:
            artwork = Artwork(**data)
            good_rows.append(artwork.model_dump())
        except Exception as error:
            reasons = "; ".join(e["msg"] for e in error.errors()) if hasattr(error, "errors") else str(error)
            record = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            record["reject_reason"] = reasons
            rejected.append(record)

    with open(REJECTED_FILE, "w", encoding="utf-8") as f:
        json.dump(rejected, f, ensure_ascii=False, indent=2, default=str)

    good_df = pd.DataFrame(good_rows)
    print("Rows in:", len(df))
    print("Good rows:", len(good_df))
    print("Rejected rows:", len(rejected))
    write_quality_report(df, good_df, rejected)
    return good_df, rejected


if __name__ == "__main__":
    from pipeline.transform import transform

    with open(RAW_FILE, encoding="utf-8") as f:
        raw_df = pd.DataFrame(json.load(f)["data"])

    df = transform(raw_df)
    good_df, rejected = validate(df)
    for r in rejected[:5]:
        print(r["id"], "->", r["reject_reason"])