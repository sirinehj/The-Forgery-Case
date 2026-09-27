"""
Merges case_documents.csv into your existing corpus_automated.csv.

Your existing corpus (5 real paintings' primary/wiki/comparanda rows) has
no evidence_role column yet. This script adds one, tagging every existing
row as neutral_background (they're real reference material, not evidence
for or against any case's verdict), then appends the 10 new case-specific
rows, which already carry the correct evidence_role.

Run from the same folder as both CSVs:
    python merge_into_corpus.py corpus_automated.csv case_documents.csv
Outputs:
    corpus_merged.csv
"""

import csv
import sys

OUTPUT_FIELDNAMES = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "title", "artist", "date", "museum", "medium", "culture",
    "credit_line", "url", "text",
]


def load_rows(path, is_new_schema):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not is_new_schema:
        # existing corpus rows have no evidence_role column yet
        for row in rows:
            row["evidence_role"] = "neutral_background"

    return rows


def main():
    if len(sys.argv) != 3:
        print("Usage: python merge_into_corpus.py corpus_automated.csv case_documents.csv")
        sys.exit(1)

    existing_path, new_path = sys.argv[1], sys.argv[2]

    existing_rows = load_rows(existing_path, is_new_schema=False)
    new_rows = load_rows(new_path, is_new_schema=True)

    all_rows = existing_rows + new_rows

    with open("corpus_merged.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row.get(k, "") for k in OUTPUT_FIELDNAMES})

    print(f"[OK] {len(existing_rows)} existing rows + {len(new_rows)} new rows "
          f"-> corpus_merged.csv ({len(all_rows)} total)")


if __name__ == "__main__":
    main()