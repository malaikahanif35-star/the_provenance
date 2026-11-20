import json

from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.validate import validate
from pipeline.load import load

SUMMARY_FILE = "data/pipeline_summary.json"


def main(total_pages=30, skip_extract=False):
    if not skip_extract:
        extract(total_pages=total_pages)

    # 2. Transform
    df = transform()
    extracted = len(df)

    good_df, rejected = validate(df)
    loaded = load(good_df)
    summary = {
        "rows_extracted": extracted,
        "rows_rejected": len(rejected),
        "rows_loaded": loaded,
    }
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\nPIPELINE SUMMARY:", summary)


if __name__ == "__main__":
    main(skip_extract=True)