"""Evaluates the Tutor Agent on tutor_eval_set.json with the app's own retrieval
and graph, against whichever LLM the environment configures (Claude by default,
or a local Ollama/OpenAI-compatible server). Writes results/tutor_eval_<label>.json.

    python -m evaluation.run_tutor_eval --label ollama-qwen2.5-3b

All metrics are rule-based and deterministic (no LLM judge), so they are
cheap and repeatable but coarse; see docs/EVALUATION.md for what they miss.
"""
import argparse
import json
import re
import time
from functools import partial
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient

from app.ai import tutor_agent
from app.ai.rag.embedder import embed_query
from app.ai.rag.ingest import ingest_knowledge_base
from app.ai.rag.retriever import retrieve

HERE = Path(__file__).parent
ABSTAIN = re.compile(
    r"not covered|outside (of )?(the |our |this )?(app|reference|material|scope|my)|"
    r"doesn'?t (cover|include|contain)|does not (cover|include|contain)|"
    r"not (part of|in|included in) (the |our |this |my )?(app|reference|material|notes)|"
    r"general knowledge|beyond (the |our |this )?(app|reference|material|scope|a1)|"
    r"no (matching )?reference|not mentioned|not (explicitly )?addressed", re.I)
EXAMPLE = re.compile(r"\*\*(.+?)\*\*|`(.+?)`|\"(.+?)\"|“(.+?)”")


def words(s):
    return re.findall(r"[a-zäöüß]+", s.lower())


def examples(answer):
    out = [next(g for g in m.groups() if g) for m in EXAMPLE.finditer(answer)]
    return [e for e in out if 1 <= len(words(e)) <= 8]


def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    cases = json.loads((HERE / "tutor_eval_set.json").read_text())["cases"][: args.limit]

    mem = QdrantClient(":memory:")
    ingest_knowledge_base(mem)
    tutor_agent.retrieve = partial(retrieve, client=mem)
    model = tutor_agent.get_chat_model()
    graph = tutor_agent.build_tutor_graph(model)
    print(f"model: {tutor_agent.get_active_model_name()}  cases: {len(cases)}")

    rows = []
    for c in cases:
        t0 = time.time()
        st = graph.invoke({"question": c["question"], "cefr_level": c["cefr_level"], "context_chunks": [],
                           "answer": "", "input_tokens": 0, "output_tokens": 0})
        ans, chunks = st["answer"], st["context_chunks"]
        topics = [k.topic_name for k in chunks]
        ctx_vocab = set(words(" ".join(k.text for k in chunks)))
        r = {"id": c["id"], "kind": c["kind"], "question": c["question"], "answer": ans, "retrieved": topics,
             "relevance": cosine(embed_query(c["question"]), embed_query(ans)),
             "abstained": bool(ABSTAIN.search(ans)), "seconds": round(time.time() - t0, 2),
             "input_tokens": st["input_tokens"], "output_tokens": st["output_tokens"]}
        if c["kind"] == "in_scope":
            r["hit_at_4"] = c["topic"] in topics
            r["rank"] = topics.index(c["topic"]) + 1 if c["topic"] in topics else None
            r["correct"] = all(any(re.search(p, ans, re.I) for p in grp) for grp in c["must"])
            ex = examples(ans)
            sup = [all(w in ctx_vocab for w in words(e)) for e in ex]
            r["examples"], r["grounded_share"] = len(ex), (sum(sup) / len(sup) if sup else None)
        rows.append(r)
        print(f"{c['id']} {'ok ' if r.get('correct') or r['abstained'] and c['kind'] != 'in_scope' else 'MISS'} "
              f"{r['seconds']}s", flush=True)

    ins = [r for r in rows if r["kind"] == "in_scope"]
    outs = [r for r in rows if r["kind"] == "out_of_scope"]
    g = [r["grounded_share"] for r in ins if r["grounded_share"] is not None]
    summary = {
        "label": args.label, "model": tutor_agent.get_active_model_name(),
        "provider": tutor_agent.settings.LLM_PROVIDER, "cases": len(rows),
        "in_scope": len(ins), "out_of_scope": len(outs),
        "retrieval_hit_at_1": float(np.mean([r["rank"] == 1 for r in ins])),
        "retrieval_hit_at_4": float(np.mean([r["hit_at_4"] for r in ins])),
        "retrieval_mrr": float(np.mean([1 / r["rank"] if r["rank"] else 0 for r in ins])),
        "correctness": float(np.mean([r["correct"] for r in ins])),
        "correctness_when_retrieved": float(np.mean([r["correct"] for r in ins if r["hit_at_4"]] or [0])),
        "relevance_mean_cosine": float(np.mean([r["relevance"] for r in rows])),
        "groundedness_example_support": float(np.mean(g)) if g else None,
        "groundedness_answers_scored": len(g),
        "out_of_scope_flagged": float(np.mean([r["abstained"] for r in outs])),
        "in_scope_falsely_flagged": float(np.mean([r["abstained"] for r in ins])),
        "median_seconds": float(np.median([r["seconds"] for r in rows])),
        "total_tokens": sum(r["input_tokens"] + r["output_tokens"] for r in rows),
    }
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / f"tutor_eval_{args.label}.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
