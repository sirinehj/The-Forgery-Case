"""
Removes the ref_klimt -> case_blue_horses_dusk link.

Reason (empirically demonstrated, not theoretical): across dense (BGE-m3),
raw BM25, and stemmed BM25 retrieval, ref_klimt chunks ranked in the top 2
results for a real Case 3 query ("who forged this painting") despite zero
actual relevance -- consistently outranking the document that names the
real forger. A "loose stylistic match" isn't worth actively degrading
retrieval quality in a corpus this small. Left unlinked, same treatment as
the da Vinci rows, rather than removed from the corpus entirely -- keep it
as background reference, just not scoped into Case 3's retrieval.

Run:
    python drop_klimt_link.py final_corpus_v2.csv
Outputs:
    final_corpus_v3.csv
"""

import csv
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python drop_klimt_link.py final_corpus_v2.csv")
        sys.exit(1)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    changed = 0
    for row in rows:
        if row["case_id"] == "ref_klimt" and row["relevant_cases"]:
            row["relevant_cases"] = ""
            changed += 1

    with open("final_corpus_v3.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] wrote {len(rows)} rows -> final_corpus_v3.csv ({changed} ref_klimt rows unlinked)")


if __name__ == "__main__":
    main()