"""
Fills the last TODO from the original manual_corpus_template.csv: Case 1's
technical_fact row. Sourced from published pigment analysis research (MoMA
in collaboration with the Rochester Institute of Technology): the sky uses
ultramarine and cobalt blue, the stars and moon use chrome yellow and zinc
yellow, and the cypress tree uses emerald green -- all pigments in ordinary
commercial use well before 1889. No anachronistic material was found.

This introduces "supports_authentic" as the fourth evidence_role value.
Cases 2 and 3 only ever needed supports_forged / red_herring /
neutral_background; Case 1 is the first row that positively supports an
"authentic" verdict rather than just being neutral background.

Run:
    python add_starry_night_technical.py final_corpus.csv
Outputs:
    final_corpus_v2.csv
"""

import csv
import sys

FIELDNAMES = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "relevant_cases", "title", "artist", "date", "museum", "medium",
    "culture", "credit_line", "url", "text",
]

NEW_ROW = {
    "doc_id": "case_starry_night_technical_001",
    "case_id": "case_starry_night",
    "source_type": "manual_verified_source",
    "document_type": "technical_fact",
    "evidence_role": "supports_authentic",
    "relevant_cases": "case_starry_night",
    "title": "The Starry Night - pigment analysis",
    "artist": "Vincent van Gogh",
    "date": "",
    "museum": "",
    "medium": "",
    "culture": "",
    "credit_line": "",
    "url": "",
    "text": (
        "Pigment analysis of The Starry Night, conducted through a "
        "collaboration between the Museum of Modern Art and the "
        "Rochester Institute of Technology, identified ultramarine and "
        "cobalt blue in the sky, chrome yellow and zinc yellow in the "
        "stars and moon, and emerald green in the cypress tree. All "
        "pigments identified were in ordinary commercial use well before "
        "1889, consistent with the painting's documented date of "
        "execution. No material inconsistent with a nineteenth-century "
        "origin has been identified."
    ),
}


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_starry_night_technical.py final_corpus.csv")
        sys.exit(1)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    rows.append(NEW_ROW)

    with open("final_corpus_v2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] wrote {len(rows)} rows -> final_corpus_v2.csv (added 1 row)")


if __name__ == "__main__":
    main()