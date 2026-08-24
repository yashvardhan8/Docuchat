"""
Lightweight RAG evaluation harness.

This is intentionally simple (no paid eval service) and checks the two
things that matter most for a portfolio demo:

  1. Retrieval relevance  — did we retrieve chunks from the expected source?
  2. Answer correctness   — manual/keyword check against an expected answer.

Concepts (explained briefly, see README for more):
  - Context precision: of the chunks retrieved, how many were actually relevant?
  - Context recall:    of the relevant chunks that exist, how many did we retrieve?
  - Faithfulness:      does the generated answer stay grounded in the retrieved context
                        (no hallucination beyond it)?
  - Answer relevance:  does the answer actually address the question asked?

Usage:
    1. Upload the document(s) referenced in questions.json via the API first.
    2. python evaluate_rag.py
"""
import json
import sys

from app.services import rag_pipeline, retriever


def load_eval_set(path: str = "questions.json") -> list[dict]:
    with open(path, "r") as f:
        return json.load(f)


def evaluate():
    eval_set = load_eval_set()
    total = len(eval_set)
    retrieval_hits = 0
    results = []

    for item in eval_set:
        question = item["question"]
        expected_source = item.get("source")

        retrieved_chunks = retriever.retrieve(question)
        sources_hit = {c["source"] for c in retrieved_chunks}
        retrieval_ok = expected_source in sources_hit if expected_source else None
        if retrieval_ok:
            retrieval_hits += 1

        answer = rag_pipeline.answer_question(question)["answer"]

        results.append(
            {
                "question": question,
                "expected_answer": item.get("expected_answer"),
                "generated_answer": answer,
                "expected_source": expected_source,
                "retrieved_sources": list(sources_hit),
                "retrieval_match": retrieval_ok,
            }
        )

    print("\n=== DocuChat RAG Evaluation ===\n")
    for r in results:
        print(f"Q: {r['question']}")
        print(f"  Expected source hit: {r['retrieval_match']}")
        print(f"  Expected answer:  {r['expected_answer']}")
        print(f"  Generated answer: {r['generated_answer']}")
        print()

    if total:
        print(f"Retrieval hit rate: {retrieval_hits}/{total} "
              f"({100 * retrieval_hits / total:.1f}%)")
    print("\nNote: answer correctness above is for manual review — this script")
    print("does not auto-grade semantic correctness (that would need an LLM-as-judge,")
    print("listed as a future improvement in the README).")


if __name__ == "__main__":
    try:
        evaluate()
    except FileNotFoundError:
        print("questions.json not found. Create one first (see backend/questions.json).")
        sys.exit(1)
