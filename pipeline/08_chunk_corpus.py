"""
Chunks final_corpus_v2.csv for indexing.

Design decision (see team briefing PDF): every document in this corpus is
currently a short, atomic paragraph making one claim (median ~9-20 words
in the sample, real Wikipedia extracts up to ~150 words). Splitting an
already-atomic claim in half would hurt, not help, both retrieval and the
Archivist's citation formatter, whose whole job is "never answer without
a source" -- one clean chunk = one clean citation.

So: documents at or under WORD_THRESHOLD stay whole (one chunk). Only a
document that actually exceeds the threshold gets split, by paragraph
first, then by sentence-grouping with a small overlap, so nothing here is
hardcoded to "this corpus is always short" -- it will do the right thing
automatically if a longer document (e.g. a fuller conservation report) is
added later.

Every chunk carries the full metadata row (case_id, evidence_role,
relevant_cases, document_type, etc.) so retrieval filtering and citation
back to the source document both work.

Run:
    python chunk_corpus.py final_corpus_v2.csv
Outputs:
    chunks.csv
"""

import csv
import re
import sys

WORD_THRESHOLD = 150   # documents at/under this word count are not split
CHUNK_TARGET = 100     # target words per chunk when splitting is needed
OVERLAP_SENTENCES = 1  # sentences repeated at the start of the next chunk

FIELDNAMES = [
    "chunk_id", "chunk_index", "doc_id", "case_id", "source_type",
    "document_type", "evidence_role", "relevant_cases", "title", "artist",
    "date", "museum", "url", "chunk_text",
]

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_long_text(text):
    """Split into ~CHUNK_TARGET-word groups of whole sentences, with a
    small sentence overlap between consecutive chunks."""
    sentences = [s for s in SENTENCE_SPLIT_RE.split(text.strip()) if s]

    chunks, current, current_words = [], [], 0
    for sentence in sentences:
        w = len(sentence.split())
        if current and current_words + w > CHUNK_TARGET:
            chunks.append(" ".join(current))
            current = current[-OVERLAP_SENTENCES:]  # carry overlap forward
            current_words = sum(len(s.split()) for s in current)
        current.append(sentence)
        current_words += w
    if current:
        chunks.append(" ".join(current))

    return chunks if chunks else [text]


def chunk_row(row):
    text = row["text"].strip()
    word_count = len(text.split())

    pieces = [text] if word_count <= WORD_THRESHOLD else split_long_text(text)

    out = []
    for i, piece in enumerate(pieces):
        out.append({
            "chunk_id": f"{row['doc_id']}_c{i}",
            "chunk_index": i,
            "doc_id": row["doc_id"],
            "case_id": row["case_id"],
            "source_type": row["source_type"],
            "document_type": row["document_type"],
            "evidence_role": row["evidence_role"],
            "relevant_cases": row["relevant_cases"],
            "title": row["title"],
            "artist": row["artist"],
            "date": row["date"],
            "museum": row["museum"],
            "url": row["url"],
            "chunk_text": piece,
        })
    return out


def main():
    if len(sys.argv) != 2:
        print("Usage: python chunk_corpus.py final_corpus_v2.csv")
        sys.exit(1)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    all_chunks = []
    for row in rows:
        all_chunks.extend(chunk_row(row))

    with open("chunks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_chunks)

    split_docs = sum(1 for row in rows if len(row["text"].split()) > WORD_THRESHOLD)
    print(f"[OK] {len(rows)} documents -> {len(all_chunks)} chunks -> chunks.csv "
          f"({split_docs} documents were long enough to split)")


if __name__ == "__main__":
    main()