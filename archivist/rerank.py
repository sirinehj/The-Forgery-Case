"""
Reranks RRF's fused shortlist with a cross-encoder (BAAI/bge-reranker-v2-m3).

Unlike dense retrieval and BM25, which score query and document
SEPARATELY and then compare, a cross-encoder takes the query and ONE
candidate document TOGETHER as a single input, so query words and
document words can directly attend to each other. That's what gives it
a real shot at cases like "forged" vs. "forgery" -- genuine language
understanding on the pair, not vector comparison or token overlap.

This is expensive, so it only ever runs on a small shortlist (RRF's top
N), never the whole corpus -- reranking fixes ORDERING among candidates
already found, it can't rescue a document neither retriever surfaced.

No extra install needed -- this uses sentence-transformers' CrossEncoder,
which you already have installed (same library that loaded BGE-m3).
bge-reranker-v2-m3 is a standard sequence-classification cross-encoder,
so it loads the same way any CrossEncoder model does; no need for the
FlagEmbedding package, which pulls in a much heavier dependency chain
(full HuggingFace `datasets` + `pyarrow`, meant for training/fine-tuning,
not inference) that can hit native DLL issues on locked-down Windows
machines.

Run:
    python rerank.py "who forged this painting" --case case_blue_horses_dusk
"""

import argparse

from sentence_transformers import CrossEncoder, SentenceTransformer
import chromadb

from rrf_search import (
    load_chunks, build_bm25, dense_ranked_ids, bm25_ranked_ids,
    reciprocal_rank_fusion, CANDIDATE_POOL_SIZE,
)

PERSIST_DIR = "./chroma_store"
COLLECTION_NAME = "archivist_documents"
DENSE_MODEL_NAME = "BAAI/bge-m3"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"
RERANK_SHORTLIST_SIZE = 10   # how many of RRF's top results actually get reranked

# Established from repeated testing (three separate queries): a genuine
# match on this corpus scores ~0.69-0.73 after sigmoid; documents the
# reranker has no real opinion on cluster flat at ~0.50-0.52, sometimes
# landing on EXACTLY 0.5000 (raw score ~0, sigmoid(0)=0.5) -- that flat
# cluster is noise, not a meaningful 2nd/3rd/4th place. 0.6 sits cleanly
# between the two: comfortably above the noise ceiling (~0.52), comfortably
# below the confident floor (~0.69) observed so far. Revisit this number
# once more queries have been tested -- three data points is a start, not
# a proof.
CONFIDENCE_THRESHOLD = 0.6


def get_reranked(query, case_filter=None, chunks_path="chunks.csv"):
    """
    Reusable core: runs dense + BM25 + RRF + reranking, returns a list of
    (chunk_id, score, row) sorted best-first, where row is the full chunk
    metadata dict. This is what citation_formatter.py (and anything else
    that needs ranked, scored chunks) should import rather than
    duplicating the retrieval pipeline.
    """
    chunks = load_chunks(chunks_path)
    chunk_lookup = {row["chunk_id"]: row for row in chunks}
    bm25, chunks = build_bm25(chunks)

    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    dense_model = SentenceTransformer(DENSE_MODEL_NAME)

    dense_ids = dense_ranked_ids(collection, dense_model, query, case_filter, CANDIDATE_POOL_SIZE)
    lexical_ids = bm25_ranked_ids(bm25, chunks, query, case_filter, CANDIDATE_POOL_SIZE)
    fused = reciprocal_rank_fusion([dense_ids, lexical_ids])

    shortlist_ids = [chunk_id for chunk_id, _ in fused[:RERANK_SHORTLIST_SIZE]]

    reranker = CrossEncoder(RERANKER_MODEL_NAME)
    pairs = [[query, chunk_lookup[cid]["chunk_text"]] for cid in shortlist_ids]
    raw_scores = reranker.predict(pairs)
    rerank_scores = [1 / (1 + pow(2.718281828, -s)) for s in raw_scores]

    reranked = sorted(zip(shortlist_ids, rerank_scores), key=lambda x: -x[1])
    return [(cid, score, chunk_lookup[cid]) for cid, score in reranked]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case", default=None)
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--chunks", default="chunks.csv")
    args = parser.parse_args()

    print(f"Loading reranker ({RERANKER_MODEL_NAME})...")
    reranked_with_rows = get_reranked(args.query, args.case, args.chunks)
    reranked = [(cid, score) for cid, score, row in reranked_with_rows]
    chunk_lookup = {cid: row for cid, score, row in reranked_with_rows}
    rrf_rank_of = {cid: i + 1 for i, (cid, score) in enumerate(reranked)}

    print(f"\nReranked query: {args.query!r}" + (f"  (case={args.case})" if args.case else ""))
    print("-" * 70)
    confident_count = 0
    for rank, (chunk_id, score) in enumerate(reranked[:args.k], start=1):
        row = chunk_lookup[chunk_id]
        tag = "CONFIDENT" if score >= CONFIDENCE_THRESHOLD else "weak/uncertain"
        if score >= CONFIDENCE_THRESHOLD:
            confident_count += 1
        print(f"{rank}. rerank_score={score:.4f} [{tag}]  (was RRF rank #{rrf_rank_of[chunk_id]})  "
              f"[{row['case_id']} | {row['evidence_role']}]")
        print(f"   {chunk_id}: {row['chunk_text'][:130]}")

    print(f"\n{confident_count} of {min(args.k, len(reranked))} results are CONFIDENT "
          f"(score >= {CONFIDENCE_THRESHOLD}). Only these should be treated as citable "
          f"evidence -- the rest are background noise, not a ranked 2nd/3rd/4th place, "
          f"and citing them as evidence would misrepresent how sure the system actually is.")


if __name__ == "__main__":
    main()