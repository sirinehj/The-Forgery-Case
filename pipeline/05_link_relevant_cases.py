"""
Adds a relevant_cases column so the Curator's search tool can pull real
stylistic/period comparanda while reasoning about a specific case, instead
of every ref_* row floating disconnected from all 3 investigations.

Mapping (judgment calls, review before relying on them):

  ref_vermeer     -> case_widows_supper
      Direct style match: Case 2's fictional painting (candlelit Dutch
      domestic interior, attributed to a minor Dutch Golden Age painter)
      sits in the same genre and period as the real Vermeer material.

  ref_klimt       -> (unlinked as of 2nd retrieval test)
      Originally linked to case_blue_horses_dusk as a loose period match,
      but retrieval testing showed this was actively harmful: across
      dense (BGE-m3), raw BM25, and stemmed BM25, ref_klimt chunks
      out-ranked the actual case evidence (the document naming the real
      forger) for a plain query about who forged the painting -- three
      independent methods, same failure. Unlinked rather than kept as a
      "loose but harmless" match. Replace with a real German
      Expressionist reference (e.g. Franz Marc, whose actual horse
      paintings would be a much stronger fit) if/when someone collects
      one -- don't relink to Klimt.

  ref_vangogh     -> case_starry_night
      Direct: same real artist, other real works. Unambiguous.

  ref_davinci_1,
  ref_davinci_2   -> (unlinked)
      Italian Renaissance devotional/portrait work has no genuine period
      or style connection to either forged case, or to Case 1. Left
      unlinked rather than forced. Decide with the team whether to keep
      this material as intentional retrieval noise (useful for testing
      that agents don't over-retrieve irrelevant material) or drop it.

Case-specific rows (case_widows_supper_*, case_blue_horses_*,
case_starry_night_*) get relevant_cases = their own case_id, so a single
filter ("relevant_cases contains X") returns everything useful for case X
in one query, including the case's own evidence.

Run:
    python link_relevant_cases.py corpus_final.csv
Outputs:
    corpus_linked.csv
"""

import csv
import sys

FIELDNAMES = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "relevant_cases", "title", "artist", "date", "museum", "medium",
    "culture", "credit_line", "url", "text",
]

REF_TO_CASE = {
    "ref_vermeer": "case_widows_supper",
    "ref_klimt": "",                         # unlinked -- see docstring, retrieval evidence
    "ref_vangogh": "case_starry_night",
    "ref_davinci_1": "",                     # intentionally unlinked
    "ref_davinci_2": "",                     # intentionally unlinked
}


def link_row(row):
    case_id = row["case_id"]

    if case_id in REF_TO_CASE:
        row["relevant_cases"] = REF_TO_CASE[case_id]
    else:
        # case_widows_supper_*, case_blue_horses_dusk_*, case_starry_night_*
        row["relevant_cases"] = case_id

    return row


def main():
    if len(sys.argv) != 2:
        print("Usage: python link_relevant_cases.py corpus_final.csv")
        sys.exit(1)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [link_row(dict(row)) for row in reader]

    with open("corpus_linked.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    unlinked = sum(1 for r in rows if r["relevant_cases"] == "")
    print(f"[OK] wrote {len(rows)} rows -> corpus_linked.csv ({unlinked} rows left unlinked)")


if __name__ == "__main__":
    main()