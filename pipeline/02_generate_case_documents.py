"""
Generates the case-specific documents for Case 2 (The Widow's Supper) and
Case 3 (Blue Horses at Dusk), as CSV rows matching the existing corpus
schema (doc_id, case_id, source_type, document_type, title, artist, date,
museum, medium, culture, credit_line, url, text) plus one new column,
evidence_role, used by the contradiction-detection rule and the eval
harness.

The two technical_fact rows are anchored to real, sourced facts:
  - Case 2: Paul Coremans's forensic investigation found phenolformaldehyde
    resins (Bakelite / Albertol) used as paint hardeners in Van Meegeren's
    forged "Vermeers" -- Bakelite is a 20th-century synthetic, proving the
    paint could not be genuinely 17th-century.
  - Case 3: Forensic pigment analysis of Beltracchi's "Red Picture with
    Horses" found titanium white, a pigment not commercially available
    until the 1920s, in a work claimed to date from 1914.
Everything else in this file is invented narrative wrapped around those
two real anchors, using the fictional names from truth.yaml.

Run:
    python generate_case_documents.py
Outputs:
    case_documents.csv
"""

import csv

FIELDNAMES = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "title", "artist", "date", "museum", "medium", "culture",
    "credit_line", "url", "text",
]

ROWS = [
    # ---------------- CASE 2: The Widow's Supper ----------------
    {
        "doc_id": "case_widows_supper_primary_001",
        "case_id": "case_widows_supper",
        "source_type": "fictional_case_document",
        "document_type": "primary_record",
        "evidence_role": "neutral_background",
        "title": "The Widow's Supper — sale record, 1952",
        "artist": "Cornelis van Leyden (attributed)",
        "date": "1952",
        "museum": "Van Doren Gallery, Amsterdam",
        "medium": "Oil on oak panel",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "In March 1952, the Van Doren Gallery in Amsterdam announced the "
            "acquisition of a previously unrecorded panel painting, The "
            "Widow's Supper, attributed on stylistic grounds to the minor "
            "Dutch Golden Age painter Cornelis van Leyden. The gallery "
            "described the work as a significant addition to van Leyden's "
            "small surviving oeuvre, noting its accomplished handling of "
            "candlelight and domestic interior space. The panel was sold "
            "later that year to a private Rotterdam collector for an "
            "undisclosed sum reported to be substantial."
        ),
    },
    {
        "doc_id": "case_widows_supper_technical_001",
        "case_id": "case_widows_supper",
        "source_type": "manual_verified_source",
        "document_type": "technical_fact",
        "evidence_role": "supports_forged",
        "title": "The Widow's Supper — forensic paint analysis, 1961",
        "artist": "Cornelis van Leyden (attributed)",
        "date": "1961",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Chemical analysis of paint samples taken from The Widow's "
            "Supper identified phenolformaldehyde resin used as a paint "
            "hardener throughout the ground and upper paint layers. "
            "Phenolformaldehyde resins are a synthetic material with no "
            "known production before the early twentieth century; their "
            "presence is inconsistent with a paint layer of genuine "
            "seventeenth-century origin. The finding was independently "
            "confirmed on a second sampling pass before being disclosed to "
            "the painting's owner."
        ),
    },
    {
        "doc_id": "case_widows_supper_primary_002",
        "case_id": "case_widows_supper",
        "source_type": "fictional_case_document",
        "document_type": "primary_record",
        "evidence_role": "supports_forged",
        "title": "The Widow's Supper — exposure record, 1961",
        "artist": "Aert de Wilde",
        "date": "1961",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Following the 1961 forensic finding, the owner of The Widow's "
            "Supper commissioned an independent inquiry, which traced the "
            "work's creation to the painter and restorer Aert de Wilde. De "
            "Wilde admitted to having painted The Widow's Supper and at "
            "least three other panels sold as rediscovered van Leyden works "
            "between 1951 and 1954, stating he had developed the "
            "hardening technique specifically to defeat the solvent-based "
            "authenticity tests used by dealers at the time."
        ),
    },
    {
        "doc_id": "case_widows_supper_expert_001",
        "case_id": "case_widows_supper",
        "source_type": "fictional_case_document",
        "document_type": "expert_opinion",
        "evidence_role": "red_herring",
        "title": "Authentication essay on The Widow's Supper, 1952",
        "artist": "Cornelis van Leyden (attributed)",
        "date": "1952",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Writing shortly after the painting's appearance on the market, "
            "the period connoisseur Willem Anthonisz described The Widow's "
            "Supper as 'an unmistakable and moving addition to van Leyden's "
            "regrettably slender output,' praising in particular its "
            "handling of light and its 'unforced, wholly period sensibility "
            "of composition.' Anthonisz's essay was widely cited by dealers "
            "as the painting changed hands over the following years."
        ),
    },
    {
        "doc_id": "case_widows_supper_provenance_001",
        "case_id": "case_widows_supper",
        "source_type": "fictional_case_document",
        "document_type": "provenance_record",
        "evidence_role": "red_herring",
        "title": "The Widow's Supper — claimed ownership history",
        "artist": "Cornelis van Leyden (attributed)",
        "date": "",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "The Van Doren Gallery's 1952 catalogue entry described The "
            "Widow's Supper as having descended within the Brandt family of "
            "Utrecht since the eighteenth century, passing by inheritance "
            "until its 'rediscovery' in a family estate sale. No inventory, "
            "estate document, or family correspondence supporting this "
            "chain was ever produced when later requested by researchers; "
            "the Brandt family named in the catalogue has not been traced."
        ),
    },

    # ---------------- CASE 3: Blue Horses at Dusk ----------------
    {
        "doc_id": "case_blue_horses_primary_001",
        "case_id": "case_blue_horses_dusk",
        "source_type": "fictional_case_document",
        "document_type": "primary_record",
        "evidence_role": "neutral_background",
        "title": "Blue Horses at Dusk — sale record, 2003",
        "artist": "Heinrich Moll (attributed)",
        "date": "2003",
        "museum": "Auktionshaus Reiner, Cologne",
        "medium": "Oil on canvas",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "In autumn 2003, Auktionshaus Reiner in Cologne sold Blue "
            "Horses at Dusk, catalogued as a previously unrecorded 1914 "
            "work by the German Expressionist Heinrich Moll, for 2.4 "
            "million euros to a private European collector. The catalogue "
            "described the painting as a rare survival from Moll's brief "
            "and celebrated pre-war period, consistent in palette and "
            "subject with his known 1913–1914 output."
        ),
    },
    {
        "doc_id": "case_blue_horses_technical_001",
        "case_id": "case_blue_horses_dusk",
        "source_type": "manual_verified_source",
        "document_type": "technical_fact",
        "evidence_role": "supports_forged",
        "title": "Blue Horses at Dusk — pigment analysis, 2014",
        "artist": "Heinrich Moll (attributed)",
        "date": "2014",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Pigment analysis of Blue Horses at Dusk identified titanium "
            "white in several areas of the sky and horses' coats. Titanium "
            "white was not commercially available as an artist's pigment "
            "until the early 1920s. Its presence in a paint layer "
            "throughout the composition, rather than as a later "
            "restoration retouch, is inconsistent with the painting's "
            "claimed 1914 date of execution."
        ),
    },
    {
        "doc_id": "case_blue_horses_primary_002",
        "case_id": "case_blue_horses_dusk",
        "source_type": "fictional_case_document",
        "document_type": "primary_record",
        "evidence_role": "supports_forged",
        "title": "Blue Horses at Dusk — exposure and conviction record, 2014",
        "artist": "Lukas Herrmann",
        "date": "2014",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Following the 2014 pigment finding, investigators traced Blue "
            "Horses at Dusk and several related 'rediscovered' Expressionist "
            "works to the painter Lukas Herrmann, who was subsequently "
            "convicted of forgery and fraud. Herrmann stated during "
            "proceedings that he mixed his own pigments to avoid detectable "
            "modern materials, but had on this occasion used a commercially "
            "purchased white paint without verifying its composition."
        ),
    },
    {
        "doc_id": "case_blue_horses_provenance_001",
        "case_id": "case_blue_horses_dusk",
        "source_type": "fictional_case_document",
        "document_type": "provenance_record",
        "evidence_role": "red_herring",
        "title": "Blue Horses at Dusk — claimed family provenance",
        "artist": "Heinrich Moll (attributed)",
        "date": "",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "The 2003 sale catalogue stated that Blue Horses at Dusk had "
            "been held since the 1920s in the collection of the Herzfeld "
            "family of Düsseldorf, supported by a photograph reportedly "
            "showing the painting hanging in a family sitting room in the "
            "1930s. The photograph, later examined during the 2014 inquiry, "
            "showed signs of artificial aging inconsistent with its claimed "
            "date, and no independent record of the Herzfeld family "
            "collection has been located."
        ),
    },
    {
        "doc_id": "case_blue_horses_dealer_001",
        "case_id": "case_blue_horses_dusk",
        "source_type": "fictional_case_document",
        "document_type": "expert_opinion",
        "evidence_role": "red_herring",
        "title": "Auction house attribution report, 2003",
        "artist": "Heinrich Moll (attributed)",
        "date": "2003",
        "museum": "",
        "medium": "",
        "culture": "",
        "credit_line": "",
        "url": "",
        "text": (
            "Auktionshaus Reiner's 2003 pre-sale attribution report "
            "concluded that Blue Horses at Dusk was 'stylistically "
            "unimpeachable as a work of Moll's 1914 period,' citing "
            "brushwork and palette consistent with two comparably dated, "
            "securely attributed paintings. The report did not include "
            "pigment or materials analysis."
        ),
    },
]


def main():
    with open("case_documents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(ROWS)
    print(f"[OK] wrote {len(ROWS)} rows -> case_documents.csv")


if __name__ == "__main__":
    main()