"""
The actual Archivist agent: citation_formatter's grounded evidence bundle,
turned into an in-character answer.

Design choice: when citation_formatter already says "insufficient_evidence",
the LLM is never called at all. Abstention here is decided deterministically
in code, before any model sees the query -- not something we hope the model
produces correctly under prompting. Stronger than "the prompt rewards it,
the verifier enforces it," and it costs nothing extra: zero risk of the
model second-guessing a correct "not in the archive" into a guess.

When there IS grounded evidence, the LLM receives ONLY citation_formatter's
safe, already-filtered output (title/date/museum/quote/confidence per
source) -- never evidence_role, never relevant_cases, never truth.yaml.
Its one job is to phrase a short in-character answer that cites what it
was given; it is not asked to judge authenticity or reveal a verdict.

Requires:
    pip install anthropic
    export ANTHROPIC_API_KEY=...   (this project's own key, not shared)

I have not run this end to end myself -- it needs your own API key, which
I don't have. Everything up to the API call is the same tested code from
citation_formatter.py; the new part (the actual model call and prompt) is
untested by me and worth checking against your team's model choice /
Anthropic API version before relying on it.

Run:
    python archivist_agent.py "phenolformaldehyde" --case case_widows_supper
    python archivist_agent.py "an unrelated nonsense query" --case case_widows_supper
"""

import argparse

import anthropic

from citation_formatter import build_response

# Check current Anthropic docs for the model string your team wants to
# standardize on -- this is a placeholder, not a verified-current value.
MODEL_NAME = "claude-sonnet-4-6"

ARCHIVIST_SYSTEM_PROMPT = """\
You are the Archivist, an expert in historical documents and provenance \
research for an art-authentication investigation.

Hard rules, no exceptions:
- Answer using ONLY the sources provided to you in this message. Never use \
outside knowledge about art history, forgeries, or any painting.
- Every claim you make must be attributable to one of the given sources. \
Cite each source by its title and date when you use it.
- Do not speculate about whether the painting is authentic or forged. You \
report what documents say; you do not render a verdict.
- Keep your answer to 2-4 sentences, in a measured, archival tone.
"""


def format_sources_for_prompt(sources):
    lines = []
    for s in sources:
        ref = f"{s.title}" + (f" ({s.date})" if s.date else "")
        lines.append(f"- [{ref}]: \"{s.quote}\"")
    return "\n".join(lines)


def answer_as_archivist(query, case_filter=None, chunks_path="chunks.csv"):
    response = build_response(query, case_filter, chunks_path)

    if response.status == "insufficient_evidence":
        return response  # finding is already "Not in the archive." -- no LLM call

    client = anthropic.Anthropic()
    user_message = (
        f"Question: {query}\n\n"
        f"Sources found in the archive:\n"
        f"{format_sources_for_prompt(response.sources)}"
    )

    reply = client.messages.create(
        model=MODEL_NAME,
        max_tokens=300,
        system=ARCHIVIST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    response.finding = reply.content[0].text
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--case", default=None)
    parser.add_argument("--chunks", default="chunks.csv")
    args = parser.parse_args()

    response = answer_as_archivist(args.query, args.case, args.chunks)
    print(f"\n[{response.status}]\n")
    print(response.finding)
    if response.sources:
        print("\nSources:")
        for s in response.sources:
            print(f"  - {s.title} ({s.date}) — confidence {s.confidence_score}")
    if response.caveats:
        print("\nCaveats:", "; ".join(response.caveats))


if __name__ == "__main__":
    main()