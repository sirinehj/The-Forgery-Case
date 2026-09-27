"""
Turns reranked, scored chunks into the Archivist's actual output contract:
a Pydantic object with finding, confidence, sources[], caveats[] -- the
exact shape your brief specifies for every agent's output.

CRITICAL SAFETY RULE, not a style choice:
evidence_role (supports_forged / supports_authentic / red_herring /
neutral_background) and relevant_cases are metadata WE attached for our
own testing, derived from the sealed truth.yaml. If either field ever
reaches an LLM's context -- even just inside a tool's return value the
model reads before writing its answer -- that IS a truth.yaml leak, the
exact thing the brief calls "the single biggest security boundary." A
field literally named supports_forged sitting in a tool result is a
verdict leak wearing a different name.

So: Citation below carries ONLY bibliographic/content fields (title,
date, museum, url, the actual quoted text, and the retrieval confidence
score, which describes retrieval quality, not truth). It does NOT carry
evidence_role or relevant_cases, and never should.

The Archivist still does not decide truth here -- if a confidently
retrieved document happens to be a red herring, it gets cited like
anything else. Evaluating red herrings is the Curator's/player's job,
not something the Archivist hides or reveals by filtering on
evidence_role.

Run:
    python citation_formatter.py "your query" --case case_widows_supper
"""

import argparse
import json

from pydantic import BaseModel

from rerank import get_reranked, CONFIDENCE_THRESHOLD


class Citation(BaseModel):
    chunk_id: str
    title: str
    date: str = ""
    museum: str = ""
    url: str = ""
    quote: str
    confidence_score: float


class ArchivistResponse(BaseModel):
    query: str
    case_id: str | None
    status: str          # "grounded" | "insufficient_evidence"
    finding: str          # placeholder until the LLM call is wired in -- see note below
    sources: list[Citation]
    caveats: list[str]


def format_citation(chunk_id, score, row):
    return Citation(
        chunk_id=chunk_id,
        title=row.get("title", ""),
        date=row.get("date", ""),
        museum=row.get("museum", ""),
        url=row.get("url", ""),
        quote=row["chunk_text"],
        confidence_score=round(score, 4),
        # NOTE: evidence_role and relevant_cases are deliberately never
        # read from `row` here -- see module docstring.
    )


def build_response(query, case_filter=None, chunks_path="chunks.csv"):
    reranked = get_reranked(query, case_filter, chunks_path)

    confident = [(cid, score, row) for cid, score, row in reranked if score >= CONFIDENCE_THRESHOLD]
    weak_count = len(reranked) - len(confident)

    caveats = []
    if weak_count:
        caveats.append(
            f"{weak_count} additional weak/uncertain match(es) were found and excluded "
            f"from citation (below the retrieval confidence threshold)."
        )

    if not confident:
        return ArchivistResponse(
            query=query,
            case_id=case_filter,
            status="insufficient_evidence",
            finding="Not in the archive.",  # the Archivist's hard rule from the brief
            sources=[],
            caveats=caveats,
        )

    citations = [format_citation(cid, score, row) for cid, score, row in confident]
    return ArchivistResponse(
        query=query,
        case_id=case_filter,
        status="grounded",
        # Placeholder: writing the actual in-character sentence from these
        # citations is the LLM call's job (next step), not this formatter's.
        # This deterministic tool's job stops at "here is what's grounded."
        finding=f"[LLM writes the in-character answer here, citing {len(citations)} source(s)]",
        sources=citations,
        caveats=caveats,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case", default=None)
    parser.add_argument("--chunks", default="chunks.csv")
    args = parser.parse_args()

    response = build_response(args.query, args.case, args.chunks)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()