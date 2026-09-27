# The Forgery Case — Archivist

Corpus, retrieval pipeline, and citation-grounded agent for the Archivist
component of *The Forgery Case*.

## Structure

```
pipeline/     corpus-building scripts, numbered in the order they must run
archivist/    the actual Archivist: hybrid retrieval + citation + LLM agent
tools/        ad hoc debugging helpers (not part of the pipeline or agent)
cases/        sealed truth.yaml per case -- never read by the agent itself
data/
  interim/    intermediate corpus files, one per pipeline stage
  processed/  chunks.csv -- final output, what gets embedded
```

## Setup

```
pip install -r requirements.txt
```

`ANTHROPIC_API_KEY` must be set as an environment variable for
`archivist/archivist_agent.py` -- never commit it.

## Rebuilding the corpus from scratch

Run the pipeline scripts in order (each takes the previous one's CSV
output):

```
python pipeline/01_collect_corpus_data.py
python pipeline/02_generate_case_documents.py
python pipeline/03_merge_into_corpus.py
python pipeline/04_fix_case_ids.py          data/interim/<merged>.csv
python pipeline/05_link_relevant_cases.py    data/interim/<fixed>.csv
python pipeline/06_add_starry_night_technical.py  data/interim/<linked>.csv
python pipeline/07_drop_klimt_link.py        data/interim/final_corpus_v2.csv
python pipeline/08_chunk_corpus.py           data/interim/final_corpus_v3.csv
python pipeline/09_build_vector_store.py     data/processed/chunks.csv
```

(Check each script's own docstring for its exact expected input filename
-- this list is the order, not copy-paste-exact commands, since a few
scripts were run against intermediate filenames during development.)

## Using the Archivist

```
python archivist/archivist_agent.py "your question" --case case_widows_supper
```

## Notes

- `cases/*.yaml` are sealed: the verdict, evidence, and red herrings for
  each case. Never read by the agent at runtime -- see each file's own
  `internal_basis_note` for why.
- `evidence_role` and `relevant_cases` metadata (in `data/`) are for our
  own testing/evaluation only and are deliberately stripped before
  anything reaches the LLM -- see `archivist/citation_formatter.py`.
