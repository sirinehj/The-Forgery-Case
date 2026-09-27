"""
Reorganizes the forgery_case project into a clean, GitHub-ready layout.
Cross-platform (uses shutil, not shell mv/move) -- works the same on
Windows PowerShell, macOS, or Linux.

Run from inside the forgery_case folder itself:
    python reorganize.py

Safe to re-run: skips any file that's already been moved (not found at
its old path), and creates target folders as needed. Does NOT touch
venv/, chroma_store/, or __pycache__/ -- those get .gitignored, not moved.
"""

import os
import shutil

# old_path -> new_path, relative to the project root
MOVES = {
    # pipeline scripts -- numbered so run order is obvious to anyone
    # cloning the repo, without needing to read every file first
    "collect_corpus_data.py":        "pipeline/01_collect_corpus_data.py",
    "generate_case_documents.py":    "pipeline/02_generate_case_documents.py",
    "merge_into_corpus.py":          "pipeline/03_merge_into_corpus.py",
    "fix_case_id.py":                "pipeline/04_fix_case_ids.py",   # renamed for consistency
    "link_relevant_cases.py":        "pipeline/05_link_relevant_cases.py",
    "add_starry_night_technical.py": "pipeline/06_add_starry_night_technical.py",
    "drop_klimt_link.py":            "pipeline/07_drop_klimt_link.py",
    "chunk_corpus.py":               "pipeline/08_chunk_corpus.py",
    "build_vector_store.py":         "pipeline/09_build_vector_store.py",

    # the Archivist itself -- retrieval, citation, and the agent
    "rrf_search.py":                 "archivist/rrf_search.py",
    "rerank.py":                     "archivist/rerank.py",
    "citation_formatter.py":         "archivist/citation_formatter.py",
    "archivist_agent.py":            "archivist/archivist_agent.py",

    # dev/debug helper, not part of the actual pipeline or agent
    "query_test.py":                 "tools/query_test.py",

    # sealed case files
    "case_starry_night_truth.yaml":     "cases/case_starry_night_truth.yaml",
    "case_widows_supper_truth.yaml":    "cases/case_widows_supper_truth.yaml",
    "case_blue_horses_dusk_truth.yaml": "cases/case_blue_horses_dusk_truth.yaml",

    # data, by pipeline stage
    "case_documents.csv":   "data/interim/case_documents.csv",
    "final_corpus.csv":     "data/interim/final_corpus.csv",
    "final_corpus_v2.csv":  "data/interim/final_corpus_v2.csv",
    "final_corpus_v3.csv":  "data/interim/final_corpus_v3.csv",
    "chunks.csv":           "data/processed/chunks.csv",
}


def main():
    moved, skipped = 0, 0
    for old, new in MOVES.items():
        if not os.path.exists(old):
            print(f"  skip (not found, already moved?): {old}")
            skipped += 1
            continue
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.move(old, new)
        print(f"  moved: {old} -> {new}")
        moved += 1

    print(f"\n[OK] {moved} files moved, {skipped} skipped")
    print("Note: data/raw/ is left for you to create manually if you keep the")
    print("original corpus_automated.csv / corpus_manual_template.csv anywhere --")
    print("they weren't in your directory listing, so this script can't find them.")


if __name__ == "__main__":
    main()