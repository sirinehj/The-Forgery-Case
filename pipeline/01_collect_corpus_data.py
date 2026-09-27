"""
Data collection script for "The Forgery Case" — Archivist corpus.

Collects:
    1. Exact primary records for the 5 anchor paintings
    2. Wikipedia descriptions as secondary/context sources
    3. Met Museum comparanda for each artist
    4. MoMA comparanda for Van Gogh
    5. Manual technical-fact placeholders for the Scientist dataset

Outputs:
    corpus_automated.csv
    corpus_manual_template.csv

Install:
    pip install requests

Run:
    python collect_corpus.py
"""

import csv
import io
import re
import time
import requests


# ============================================================
# API / DATA SOURCES
# ============================================================

MET_SEARCH_URL = (
    "https://collectionapi.metmuseum.org/public/collection/v1/search"
)

MET_OBJECT_URL = (
    "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
)

MOMA_ARTWORKS_CSV = (
    "https://raw.githubusercontent.com/MuseumofModernArt/"
    "collection/main/Artworks.csv"
)

WIKI_SUMMARY_URL = (
    "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
)


# ============================================================
# THE 5 ANCHOR PAINTINGS
# ============================================================

CASES = [

    {
        "case_id": "case_vermeer",
        "painting": "Girl with a Pearl Earring",
        "artist": "Johannes Vermeer",
        "year": "c. 1665",
        "museum": "Mauritshuis",
        "museum_url": (
            "https://www.mauritshuis.nl/en/our-collection/"
            "artworks/670-girl-with-a-pearl-earring"
        ),
        "wiki_title": "Girl with a Pearl Earring",
        "medium": "Oil on canvas",
    },

    {
        "case_id": "case_davinci_1",
        "painting": "The Last Supper",
        "artist": "Leonardo da Vinci",
        "year": "1495–1498",
        "museum": "Santa Maria delle Grazie",
        "museum_url": (
            "https://cenacolovinciano.org/en/"
        ),
        "wiki_title": "The Last Supper (Leonardo)",
        "medium": "Tempera and oil on gesso, pitch and mastic on plaster",
    },

    {
        "case_id": "case_davinci_2",
        "painting": "Mona Lisa",
        "artist": "Leonardo da Vinci",
        "year": "1503–1519",
        "museum": "Louvre",
        "museum_url": (
            "https://collections.louvre.fr/ark:/53355/cl010066723"
        ),
        "wiki_title": "Mona Lisa",
        "medium": "Oil on poplar panel",
    },

    {
        "case_id": "case_vangogh",
        "painting": "The Starry Night",
        "artist": "Vincent van Gogh",
        "year": "1889",
        "museum": "Museum of Modern Art",
        "museum_url": (
            "https://www.moma.org/collection/works/79802"
        ),
        "wiki_title": "The Starry Night",
        "medium": "Oil on canvas",
    },

    {
        "case_id": "case_klimt",
        "painting": "The Kiss",
        "artist": "Gustav Klimt",
        "year": "1907–1908",
        "museum": "Belvedere",
        "museum_url": (
            "https://www.belvedere.at/en/"
        ),
        "wiki_title": "The Kiss (Klimt)",
        "medium": "Oil and gold leaf on canvas",
    },
]


# Number of comparison works per artist
MAX_COMPARANDA_PER_ARTIST = 6


# ============================================================
# CSV STRUCTURE
# ============================================================

FIELDNAMES = [
    "doc_id",
    "case_id",
    "source_type",
    "document_type",
    "title",
    "artist",
    "date",
    "museum",
    "medium",
    "culture",
    "credit_line",
    "url",
    "text",
]


# ============================================================
# HELPERS
# ============================================================

def clean_text(text):
    """Normalize whitespace."""
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def make_doc_id(case_id, source_type, number):
    return f"{case_id}_{source_type}_{number:03d}"


def safe_get(url, params=None, timeout=30):
    """GET request with basic error handling."""
    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "The-Forgery-Case/1.0 "
                    "(educational research corpus)"
                )
            },
        )

        response.raise_for_status()
        return response

    except requests.RequestException as e:
        print(f"[ERROR] {url}")
        print(f"       {e}")
        return None


# ============================================================
# 1. EXACT PRIMARY RECORDS
# ============================================================

def fetch_anchor_records():
    """
    Create one authoritative primary record for each exact painting.

    These URLs point to the institution responsible for the artwork.
    """

    rows = []

    for i, case in enumerate(CASES, start=1):

        text = (
            f"{case['painting']} by {case['artist']}. "
            f"Dated {case['year']}. "
            f"Medium: {case['medium']}. "
            f"Collection: {case['museum']}."
        )

        rows.append({
            "doc_id": make_doc_id(
                case["case_id"],
                "primary",
                i
            ),
            "case_id": case["case_id"],
            "source_type": "primary_museum",
            "document_type": "primary_record",
            "title": case["painting"],
            "artist": case["artist"],
            "date": case["year"],
            "museum": case["museum"],
            "medium": case["medium"],
            "culture": "",
            "credit_line": "",
            "url": case["museum_url"],
            "text": text,
        })

    return rows


# ============================================================
# 2. WIKIPEDIA DESCRIPTION
# ============================================================

def fetch_wikipedia_records():
    """
    Fetch the actual Wikipedia article about each painting.

    This is secondary context, NOT the authoritative museum record.
    """

    rows = []

    for i, case in enumerate(CASES, start=1):

        title = case["wiki_title"].replace(" ", "_")

        url = WIKI_SUMMARY_URL.format(title)

        response = safe_get(url)

        if response is None:
            continue

        try:
            data = response.json()

        except ValueError:
            print(f"[wiki] invalid JSON for {case['painting']}")
            continue

        extract = clean_text(
            data.get("extract", "")
        )

        if not extract:
            continue

        rows.append({
            "doc_id": make_doc_id(
                case["case_id"],
                "wiki",
                i
            ),
            "case_id": case["case_id"],
            "source_type": "wikipedia",
            "document_type": "secondary_description",
            "title": case["painting"],
            "artist": case["artist"],
            "date": case["year"],
            "museum": case["museum"],
            "medium": case["medium"],
            "culture": "",
            "credit_line": "",
            "url": data.get("content_urls", {})
                         .get("desktop", {})
                         .get("page", ""),
            "text": extract,
        })

        print(f"[wiki] collected: {case['painting']}")

        time.sleep(0.3)

    return rows


# ============================================================
# 3. MET COMPARANDA
# ============================================================

def fetch_met_comparanda(
    case,
    max_results=MAX_COMPARANDA_PER_ARTIST
):
    """
    Find other works by the same artist in the Met collection.

    IMPORTANT:
    These are COMPARANDA, not records of the anchor painting.
    """

    rows = []

    response = safe_get(
        MET_SEARCH_URL,
        params={
            "q": case["artist"],
            "hasImages": "true",
        },
        timeout=30,
    )

    if response is None:
        return rows

    try:
        object_ids = (
            response.json().get("objectIDs") or []
        )

    except ValueError:
        return rows

    count = 0

    for object_id in object_ids:

        if count >= max_results:
            break

        time.sleep(0.2)

        response = safe_get(
            MET_OBJECT_URL.format(object_id),
            timeout=30,
        )

        if response is None:
            continue

        try:
            obj = response.json()

        except ValueError:
            continue

        artist_name = (
            obj.get("artistDisplayName") or ""
        )

        if case["artist"].lower() not in artist_name.lower():
            continue

        title = clean_text(
            obj.get("title", "")
        )

        date = clean_text(
            obj.get("objectDate", "")
        )

        medium = clean_text(
            obj.get("medium", "")
        )

        culture = clean_text(
            obj.get("culture", "")
        )

        credit_line = clean_text(
            obj.get("creditLine", "")
        )

        text = (
            f"{title} by {artist_name}. "
            f"Date: {date}. "
            f"Medium: {medium}. "
            f"Culture: {culture}. "
            f"Credit line: {credit_line}."
        )

        rows.append({
            "doc_id": make_doc_id(
                case["case_id"],
                "met_comparanda",
                count + 1
            ),
            "case_id": case["case_id"],
            "source_type": "met_api",
            "document_type": "comparanda",
            "title": title,
            "artist": artist_name,
            "date": date,
            "museum": "The Metropolitan Museum of Art",
            "medium": medium,
            "culture": culture,
            "credit_line": credit_line,
            "url": obj.get("objectURL", ""),
            "text": text,
        })

        count += 1

    print(
        f"[met] {case['painting']}: "
        f"{count} comparanda"
    )

    return rows


# ============================================================
# 4. MOMΑ DATASET
# ============================================================

def fetch_moma_van_gogh(
    max_results=MAX_COMPARANDA_PER_ARTIST
):
    """
    Pull Van Gogh records from MoMA's public dataset.

    These are comparison works, not necessarily The Starry Night.
    """

    rows = []

    response = safe_get(
        MOMA_ARTWORKS_CSV,
        timeout=60,
    )

    if response is None:
        return rows

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    count = 0

    for row in reader:

        if count >= max_results:
            break

        artist = row.get("Artist") or ""

        if "gogh" not in artist.lower():
            continue

        title = clean_text(
            row.get("Title", "")
        )

        date = clean_text(
            row.get("Date", "")
        )

        medium = clean_text(
            row.get("Medium", "")
        )

        credit_line = clean_text(
            row.get("CreditLine", "")
        )

        text = (
            f"{title} by {artist}. "
            f"Date: {date}. "
            f"Medium: {medium}. "
            f"Credit line: {credit_line}."
        )

        rows.append({
            "doc_id": make_doc_id(
                "case_vangogh",
                "moma_comparanda",
                count + 1
            ),
            "case_id": "case_vangogh",
            "source_type": "moma_dataset",
            "document_type": "comparanda",
            "title": title,
            "artist": artist,
            "date": date,
            "museum": "Museum of Modern Art",
            "medium": medium,
            "culture": "",
            "credit_line": credit_line,
            "url": row.get("URL", ""),
            "text": text,
        })

        count += 1

    print(
        f"[moma] Van Gogh: {count} comparanda"
    )

    return rows


# ============================================================
# 5. TECHNICAL FACT TEMPLATE
# ============================================================

def technical_template():
    """
    Creates a separate dataset for the Scientist.

    DO NOT invent pigment dates here.

    These rows are deliberately left for verified scientific /
    conservation sources.
    """

    rows = []

    for i, case in enumerate(CASES, start=1):

        rows.append({
            "doc_id": make_doc_id(
                case["case_id"],
                "technical",
                i
            ),
            "case_id": case["case_id"],
            "source_type": "manual_verified_source",
            "document_type": "technical_fact",
            "title": (
                f"{case['painting']} — "
                "technical / conservation evidence"
            ),
            "artist": case["artist"],
            "date": "",
            "museum": case["museum"],
            "medium": "",
            "culture": "",
            "credit_line": "",
            "url": "",
            "text": (
                "TODO: add a verified conservation, "
                "technical examination, pigment or "
                "materials source. Do not invent this fact."
            ),
        })

    return rows


# ============================================================
# 6. WRITE CSV
# ============================================================

def write_csv(path, rows):

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"[OK] wrote {len(rows)} rows -> {path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    automated_rows = []

    print("\n=== EXACT PRIMARY RECORDS ===")
    automated_rows.extend(
        fetch_anchor_records()
    )

    print("\n=== WIKIPEDIA DESCRIPTIONS ===")
    automated_rows.extend(
        fetch_wikipedia_records()
    )

    print("\n=== MET COMPARANDA ===")

    for case in CASES:

        automated_rows.extend(
            fetch_met_comparanda(case)
        )

    print("\n=== MoMA VAN GOGH ===")

    automated_rows.extend(
        fetch_moma_van_gogh()
    )

    print("\n=== WRITING AUTOMATED CORPUS ===")

    write_csv(
        "corpus_automated.csv",
        automated_rows
    )

    print("\n=== WRITING TECHNICAL TEMPLATE ===")

    write_csv(
        "corpus_manual_template.csv",
        technical_template()
    )

    print("\n=== SUMMARY ===")

    print(
        f"Total automated documents: "
        f"{len(automated_rows)}"
    )

    for case in CASES:

        count = sum(
            1
            for row in automated_rows
            if row["case_id"] == case["case_id"]
        )

        print(
            f"  {case['painting']}: "
            f"{count} documents"
        )


if __name__ == "__main__":
    main()