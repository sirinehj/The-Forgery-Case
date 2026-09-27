"""
Combines dense retrieval (Chroma + BGE-m3, already built by
build_vector_store.py) and lexical retrieval (BM25 over chunks.csv) into
one ranked list, using Reciprocal Rank Fusion (RRF).

RRF combines RANKS, not raw scores -- this matters because cosine
distance (dense) and BM25 scores live on completely different, unrelated
scales, so averaging raw scores would be meaningless. RRF sidesteps that
by only caring about each document's POSITION in each ranked list:

    score(d) = sum over retrievers r of  1 / (k + rank_r(d))

A document ranked consistently well by both retrievers beats a document
that's #1 in only one and nearly invisible in the other -- this is
exactly what makes RRF useful for hybrid search: it favors documents both
signals agree on.

Run:
    python rrf_search.py "your query" --case case_widows_supper
"""

import argparse
import csv
import re

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "./chroma_store"
COLLECTION_NAME = "archivist_documents"
MODEL_NAME = "BAAI/bge-m3"
CANDIDATE_POOL_SIZE = 20   # how many results to pull from EACH retriever before fusing
RRF_K = 60                  # standard RRF constant

STOPWORDS = {
    "a", "an", "the", "this", "that", "these", "those", "who", "what",
    "when", "where", "why", "how", "is", "are", "was", "were", "be",
    "been", "being", "of", "in", "on", "at", "to", "for", "and", "or",
    "but", "with", "by", "from", "as", "it", "its",
}


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def reciprocal_rank_fusion(ranked_lists, k=RRF_K):
    scores = {}
    for ranked_ids in ranked_lists:
        for rank, doc_id in enumerate(ranked_ids, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


def load_chunks(path="chunks.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_bm25(chunks):
    tokenized = [tokenize(row["chunk_text"]) for row in chunks]
    return BM25Okapi(tokenized), chunks


def bm25_ranked_ids(bm25, chunks, query, case_filter, pool_size):
    scores = bm25.get_scores(tokenize(query))
    order = sorted(range(len(chunks)), key=lambda i: -scores[i])
    ids = []
    for i in order:
        if case_filter and chunks[i]["relevant_cases"] != case_filter:
            continue
        ids.append(chunks[i]["chunk_id"])
        if len(ids) >= pool_size:
            break
    return ids


def dense_ranked_ids(collection, model, query, case_filter, pool_size):
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    where = {"relevant_cases": case_filter} if case_filter else None
    results = collection.query(query_embeddings=query_embedding, n_results=pool_size, where=where)
    return results["ids"][0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case", default=None)
    parser.add_argument("-k", type=int, default=5, help="final results to show")
    parser.add_argument("--chunks", default="chunks.csv")
    args = parser.parse_args()

    chunks = load_chunks(args.chunks)
    chunk_lookup = {row["chunk_id"]: row for row in chunks}
    bm25, chunks = build_bm25(chunks)

    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)

    dense_ids = dense_ranked_ids(collection, model, args.query, args.case, CANDIDATE_POOL_SIZE)
    lexical_ids = bm25_ranked_ids(bm25, chunks, args.query, args.case, CANDIDATE_POOL_SIZE)

    fused = reciprocal_rank_fusion([dense_ids, lexical_ids])

    print(f"\nRRF query: {args.query!r}" + (f"  (case={args.case})" if args.case else ""))
    print(f"(dense pool: {len(dense_ids)} | lexical pool: {len(lexical_ids)})")
    print("-" * 70)
    for rank, (chunk_id, score) in enumerate(fused[:args.k], start=1):
        row = chunk_lookup[chunk_id]
        d_rank = dense_ids.index(chunk_id) + 1 if chunk_id in dense_ids else "-"
        l_rank = lexical_ids.index(chunk_id) + 1 if chunk_id in lexical_ids else "-"
        print(f"{rank}. rrf={score:.5f}  dense_rank={d_rank}  bm25_rank={l_rank}  "
              f"[{row['case_id']} | {row['evidence_role']}]")
        print(f"   {chunk_id}: {row['chunk_text'][:130]}")


if __name__ == "__main__":
    main()