import argparse
import json
import os

import pandas as pd

from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.validate import validate

RAW_FILE = "data/raw_artworks.json"


def load_raw():
    """Saved raw file se artworks ki list nikalta hai."""
    with open(RAW_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        raw = raw["data"]
    return pd.DataFrame(raw)


def main():
    parser = argparse.ArgumentParser(description="the_provenance ETL pipeline")
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="API call skip karo aur purani data/raw_artworks.json use karo",
    )
    args = parser.parse_args()

    os.makedirs("data/rejected", exist_ok=True)

    # Step 1: Extract
    if args.skip_extract:
        print("Step 1/3: Extract skipped (using saved raw file)")
        raw_df = load_raw()
    else:
        print("Step 1/3: Extract")
        extract()
        raw_df = load_raw()

    # Step 2: Transform
    print("Step 2/3: Transform")
    df = transform(raw_df)

    # Step 3: Validate
    print("Step 3/3: Validate")
    good_df, rejected = validate(df)
    good_df.to_csv("data/validated_artworks.csv", index=False)
    print("Validated data saved: data/validated_artworks.csv")

    # Step 4: Load 

if __name__ == "__main__":
    main()