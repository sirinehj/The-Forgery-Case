"""
Builds the Archivist's vector store: embeds every chunk in chunks.csv with
BGE-m3 and stores it in a persistent ChromaDB collection, full metadata
attached to every chunk so retrieval can be filtered later (e.g. "only
chunks where relevant_cases contains case_widows_supper").

This is the DENSE half of your hybrid retrieval. BM25 (lexical) is a
separate index, built directly from chunks.csv, not covered by this
script -- that's the next piece to build. The two get combined at query
time with RRF fusion, per the brief.

IMPORTANT: this only ever reads chunks.csv. Never point this script at a
truth.yaml file or embed its contents -- the sealed verdict must never
enter any agent's retrievable context, per the brief's core security rule.

Install (one time):
    pip install chromadb sentence-transformers

Run:
    python build_vector_store.py chunks.csv
Produces:
    ./chroma_store/  (persistent on disk -- re-running is idempotent,
    rows are upserted by chunk_id, not duplicated)
"""

import csv
import sys

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "archivist_documents"
PERSIST_DIR = "./chroma_store"
MODEL_NAME = "BAAI/bge-m3"
BATCH_SIZE = 32

# Metadata fields to keep on every chunk (everything needed to filter at
# query time and to cite back to the source document).
METADATA_FIELDS = [
    "doc_id", "case_id", "source_type", "document_type", "evidence_role",
    "relevant_cases", "title", "artist", "date", "museum", "url",
]


def load_chunks(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def batched(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    if len(sys.argv) != 2:
        print("Usage: python build_vector_store.py chunks.csv")
        sys.exit(1)

    chunks = load_chunks(sys.argv[1])
    print(f"Loaded {len(chunks)} chunks from {sys.argv[1]}")

    print(f"Loading embedding model ({MODEL_NAME})... this downloads the "
          f"model on first run and may take a few minutes.")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    total = 0
    for batch in batched(chunks, BATCH_SIZE):
        ids = [row["chunk_id"] for row in batch]
        documents = [row["chunk_text"] for row in batch]
        metadatas = [{k: row.get(k, "") or "" for k in METADATA_FIELDS} for row in batch]

        embeddings = model.encode(
            documents,
            normalize_embeddings=True,   # required for cosine similarity
            show_progress_bar=False,
        ).tolist()

        # upsert, not add: safe to re-run this script after editing chunks.csv
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        total += len(batch)
        print(f"  embedded {total}/{len(chunks)}")

    print(f"[OK] {collection.count()} chunks now in Chroma collection "
          f"'{COLLECTION_NAME}' at {PERSIST_DIR}")

    # Quick sanity check: run one real query and print what comes back,
    # so you can see immediately whether retrieval is doing something
    # sensible before wiring it into the Archivist agent.
    print("\n--- sanity check query ---")
    test_query = "pigment inconsistent with the claimed date of the painting"
    query_embedding = model.encode([test_query], normalize_embeddings=True).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=3)

    for doc_id, doc_text, meta in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0]
    ):
        print(f"  [{meta['case_id']} | {meta['evidence_role']}] {doc_id}")
        print(f"    {doc_text[:120]}...")


if __name__ == "__main__":
    main()