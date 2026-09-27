"""
Ad-hoc retrieval testing against the persisted Chroma collection, without
re-embedding the whole corpus. Use this to sanity-check retrieval quality
before wiring the Archivist's actual search tool.

Run:
    python query_test.py "your query here"
    python query_test.py "your query here" --case case_widows_supper
    python query_test.py "your query here" -k 5
"""

import argparse

import chromadb
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "./chroma_store"
COLLECTION_NAME = "archivist_documents"
MODEL_NAME = "BAAI/bge-m3"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case", default=None,
                         help="Filter to chunks whose relevant_cases matches this case_id "
                              "(includes the case's own evidence, since case-specific rows "
                              "have relevant_cases set to their own case_id)")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([args.query], normalize_embeddings=True).tolist()

    where = {"relevant_cases": args.case} if args.case else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=args.k,
        where=where,
    )

    print(f"\nQuery: {args.query!r}" + (f"  (filtered to case={args.case})" if args.case else ""))
    print("-" * 70)
    if not results["ids"][0]:
        print("  (no results -- check the --case filter matches a real relevant_cases value)")
        return

    for rank, (doc_id, doc_text, meta, dist) in enumerate(zip(
        results["ids"][0], results["documents"][0],
        results["metadatas"][0], results["distances"][0]
    ), start=1):
        print(f"{rank}. [{meta['case_id']} | {meta['evidence_role']}] "
              f"dist={dist:.4f}  {doc_id}")
        print(f"   {doc_text[:150]}")


if __name__ == "__main__":
    main()