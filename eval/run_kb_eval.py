"""Check every suggested question against the knowledge base.

For each question in suggestions.py it checks:
  1. Retrieval: did the doc that answers it come back in the top-k chunks?
  2. Answer: does the answer contain the expected facts, without contradicting them?
     (graded by an LLM judge at temperature 0)

Run from the repo root after editing knowledge_base/, the chunker, the system
prompt, or suggestions.py:

    python3 eval/run_kb_eval.py              # default top-k from config
    python3 eval/run_kb_eval.py --top-k 5 --out eval/results.json

Costs a few cents per run (gpt-4o-mini answers, gpt-4o judge).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
import rag_engine  # noqa: E402
from suggestions import SUGGESTIONS, HALLUCINATION_BAIT  # noqa: E402

JUDGE_MODEL = "gpt-4o"
PASS_COVERAGE = 0.75

JUDGE_PROMPT = """You grade answers from a customer-support chatbot.
You get a QUESTION, the EXPECTED FACTS a correct answer contains, and the bot's ANSWER.
For each expected fact, decide whether the answer states it. Paraphrase is fine; numbers, prices,
time limits and UI paths must match. Then decide whether the answer contradicts any expected fact
or states a specific number, price or time limit that conflicts with them.
Return JSON: {"facts": [{"fact": "...", "present": true|false}], "contradiction": true|false, "note": "one short sentence"}"""


def judge(question: str, facts: list[str], answer: str) -> dict:
    client = rag_engine._get_openai_client()
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": (
                f"QUESTION: {question}\n\nEXPECTED FACTS:\n"
                + "\n".join(f"- {f}" for f in facts)
                + f"\n\nANSWER:\n{answer}"
            )},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def run_one(item: dict, top_k: int) -> dict:
    expected_docs = [item["doc"]] + item.get("also", []) if "doc" in item else []
    chunks = rag_engine.retrieve(item["q"], top_k=top_k)
    sources = [c["source"] for c in chunks]
    answer = rag_engine.generate(item["q"], chunks)["answer"]
    verdict = judge(item["q"], item["facts"], answer)
    present = sum(1 for f in verdict.get("facts", []) if f.get("present"))
    coverage = present / len(item["facts"])
    return {
        "q": item["q"],
        "doc": item.get("doc", "(not in KB)"),
        "sources": sources,
        "retrieval_hit": (not expected_docs) or any(d in sources for d in expected_docs),
        "coverage": coverage,
        "contradiction": bool(verdict.get("contradiction")),
        "passed": coverage >= PASS_COVERAGE and not verdict.get("contradiction"),
        "missing": [f["fact"] for f in verdict.get("facts", []) if not f.get("present")],
        "note": verdict.get("note", ""),
        "answer": answer,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=config.TOP_K_RESULTS)
    parser.add_argument("--out", help="write full results (with answers) to this JSON file")
    args = parser.parse_args()

    rag_engine.ingest_knowledge_base()
    items = SUGGESTIONS + HALLUCINATION_BAIT
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda it: run_one(it, args.top_k), items))

    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        hit = "hit " if r["retrieval_hit"] else "MISS"
        print(f"{mark}  retrieval {hit}  {int(r['coverage'] * 100):3d}%  {r['q']}")
        if not r["passed"]:
            print(f"      expected doc: {r['doc']} | got: {', '.join(r['sources'])}")
            if r["missing"]:
                print(f"      missing: {'; '.join(r['missing'])}")
            if r["contradiction"]:
                print(f"      contradiction: {r['note']}")

    n = len(results)
    in_kb = [r for r in results if r["doc"] != "(not in KB)"]
    print(f"\ntop_k={args.top_k}  chunks={len(rag_engine._index['texts'])}")
    print(f"Answers passed:   {sum(r['passed'] for r in results)}/{n}")
    print(f"Retrieval hits:   {sum(r['retrieval_hit'] for r in in_kb)}/{len(in_kb)}")
    print(f"Contradictions:   {sum(r['contradiction'] for r in results)}")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
