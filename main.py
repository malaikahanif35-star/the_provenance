import argparse
import os

from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.validate import validate


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
        print("Step 1/3: Extract skipped")
    else:
        print("Step 1/3: Extract")
        extract()

    # Step 2: Transform
    print("Step 2/3: Transform")
    df = transform()

    # Step 3: Validate
    print("Step 3/3: Validate")
    good_df, rejected = validate(df)
    good_df.to_csv("data/validated_artworks.csv", index=False)
    print("Validated data saved: data/validated_artworks.csv")

    #load


if __name__ == "__main__":
    main()