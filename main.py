import argparse
import logging

import pandas as pd

import extract
from transform import transform, CLEAN_FILE


def main():
    parser = argparse.ArgumentParser(description="the_provenance ETL pipeline")
    parser.add_argument("--skip-extract", action="store_true",
                        help="API se dobara data na layein, saved raw file use karein")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")

    # 1. Extract
    if not args.skip_extract:
        try:
            extract.extract()
        except RuntimeError as exc:
            print("EXTRACT STOPPED:", exc)
            return

    records = extract.load_raw()
    df = pd.DataFrame(records)
    print("Raw data:", df.shape)

    # 2. Transform
    clean = transform(df)
    clean.to_csv(CLEAN_FILE, index=False)
    print("Clean data:", clean.shape, "->", CLEAN_FILE)

    # Validate code


    #load code


if __name__ == "__main__":
    main()