"""
Fixes case_id inconsistencies in the merged corpus:

1. The Starry Night's own primary_record and secondary_description rows
   were tagged case_id="case_vangogh", but Case 1's truth.yaml uses
   case_id="case_starry_night". Those rows are renamed so retrieval
   scoped to "case_starry_night" actually finds them.

2. Rows that are real background/comparanda for paintings NOT tied to
   any of the 3 investigation cases (Vermeer, both da Vincis, Klimt, and
   Van Gogh's OTHER paintings like Wheat Field with Cypresses) get their
   case_id renamed from case_<x> to ref_<x>, so "case_id" is reserved
   for the 3 real investigation cases and never confused with generic
   reference material.

3. case_widows_supper and case_blue_horses_dusk rows are left untouched
   -- they were already correct.

Run:
    python fix_case_ids.py corpus_merged.csv
Outputs:
    corpus_final.csv
"""

import csv
import sys

FIELDNAMES = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "title", "artist", "date", "museum", "medium", "culture",
    "credit_line", "url", "text",
]

# Rows whose case_id is "case_vangogh" AND document_type is one of these
# are the Starry Night's OWN case record -- rename to case_starry_night.
STARRY_NIGHT_OWN_TYPES = {"primary_record", "secondary_description"}

# Any other case_id in this set is renamed case_X -> ref_X (background,
# not tied to any of the 3 active investigation cases).
BACKGROUND_CASE_IDS = {
    "case_vermeer", "case_davinci_1", "case_davinci_2", "case_klimt",
    "case_vangogh",  # only for rows that are NOT the case's own record
}


def fix_row(row):
    old_case_id = row["case_id"]

    if old_case_id == "case_vangogh" and row["document_type"] in STARRY_NIGHT_OWN_TYPES:
        new_case_id = "case_starry_night"
    elif old_case_id in BACKGROUND_CASE_IDS:
        new_case_id = "ref_" + old_case_id[len("case_"):]
    else:
        new_case_id = old_case_id  # case_widows_supper, case_blue_horses_dusk, etc.

    if new_case_id != old_case_id:
        row["doc_id"] = row["doc_id"].replace(old_case_id, new_case_id, 1)
        row["case_id"] = new_case_id

    return row


def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_case_ids.py corpus_merged.csv")
        sys.exit(1)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [fix_row(dict(row)) for row in reader]

    with open("corpus_final.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    renamed = sum(1 for r in rows if r["case_id"].startswith("ref_") or r["case_id"] == "case_starry_night")
    print(f"[OK] wrote {len(rows)} rows -> corpus_final.csv ({renamed} rows renamed)")


if __name__ == "__main__":
    main()