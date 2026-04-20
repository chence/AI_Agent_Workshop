import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
eval_path = ROOT / "eval" / "service_eval_set.csv"
catalog_path = ROOT / "artifacts" / "service_catalog.cleaned.json"
params_path = ROOT / "params.yaml"
preds_path = ROOT / "artifacts" / "eval_predictions.json"
metrics_path = ROOT / "artifacts" / "metrics.json"


def parse_scalar(raw: str):
    value = raw.strip()
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_params(path: Path) -> dict:
    params = {}
    current_section = None
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            current_section = line.split(":", 1)[0].strip()
            params[current_section] = {}
            continue
        if current_section is None:
            continue
        key, value = line.strip().split(":", 1)
        params[current_section][key.strip()] = parse_scalar(value)
    return params


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def keyword_retrieve(query: str, catalog_df: pd.DataFrame, params: dict) -> pd.DataFrame:
    q_tokens = set(tokenize(query))
    keyword_weight = float(params["retrieval"]["keyword_weight"])
    scored_rows = []
    for _, row in catalog_df.iterrows():
        row_tokens = tokenize(str(row.get("retrieval_text", "")))
        overlap = sum(token in row_tokens for token in q_tokens)
        score = overlap * keyword_weight
        scored_rows.append({**row.to_dict(), "retrieval_score": float(score)})

    ranked = pd.DataFrame(scored_rows).sort_values(
        by=["retrieval_score", "service_name"],
        ascending=[False, True],
    )
    ranked = ranked[ranked["retrieval_score"] >= float(params["retrieval"]["min_score"])]
    return ranked.head(int(params["retrieval"]["top_k"])).reset_index(drop=True)


def predict_question(question: str, catalog_df: pd.DataFrame, params: dict) -> dict:
    retrieved = keyword_retrieve(question, catalog_df, params)
    if retrieved.empty:
        return {
            "predicted_service_name": "Unclear",
            "predicted_jurisdiction_level": "Unclear",
            "predicted_responsible_body": "Unknown",
            "confidence": float(params["agent"]["unclear_confidence"]),
            "sources": [],
            "retrieved_candidates": [],
        }

    best = retrieved.iloc[0]
    ambiguous = best["jurisdiction_level"] == "Mixed"
    if len(retrieved) > 1:
        margin = float(best["retrieval_score"]) - float(retrieved.iloc[1]["retrieval_score"])
        ambiguous = ambiguous or margin <= float(params["retrieval"]["ambiguity_margin"])

    confidence = float(params["agent"]["default_confidence"])
    if ambiguous:
        confidence = min(confidence, 0.58)

    sources = [best["source_url"]] if str(best.get("source_url", "")).strip() else []
    if params["agent"]["require_sources"] and not sources:
        return {
            "predicted_service_name": "Unclear",
            "predicted_jurisdiction_level": "Unclear",
            "predicted_responsible_body": "Unknown",
            "confidence": float(params["agent"]["unclear_confidence"]),
            "sources": [],
            "retrieved_candidates": retrieved[
                ["service_name", "jurisdiction_level", "retrieval_score"]
            ].to_dict(orient="records"),
        }

    return {
        "predicted_service_name": best["service_name"],
        "predicted_jurisdiction_level": best["jurisdiction_level"],
        "predicted_responsible_body": best["responsible_body"],
        "confidence": confidence,
        "sources": sources,
        "retrieved_candidates": retrieved[
            ["service_name", "jurisdiction_level", "retrieval_score"]
        ].to_dict(orient="records"),
    }


params = load_params(params_path)
eval_df = pd.read_csv(eval_path).head(int(params["evaluation"]["max_examples"]))
catalog_df = pd.read_json(catalog_path)

predictions = []
for _, row in eval_df.iterrows():
    pred = predict_question(row["question"], catalog_df, params)
    predictions.append(
        {
            "question": row["question"],
            "expected_service_name": row["expected_service_name"],
            "expected_jurisdiction_level": row["expected_jurisdiction_level"],
            "expected_responsible_body": row["expected_responsible_body"],
            **pred,
        }
    )

pred_df = pd.DataFrame(predictions)
preds_path.parent.mkdir(exist_ok=True)
pred_df.to_json(preds_path, orient="records", indent=2)

metrics = {
    "jurisdiction_accuracy": float(
        (pred_df["predicted_jurisdiction_level"] == pred_df["expected_jurisdiction_level"]).mean()
    ),
    "responsible_body_accuracy": float(
        (pred_df["predicted_responsible_body"] == pred_df["expected_responsible_body"]).mean()
    ),
    "source_presence_rate": float(pred_df["sources"].apply(lambda value: len(value) > 0).mean()),
    "avg_confidence": float(pred_df["confidence"].mean()),
    "n_examples": int(len(pred_df)),
    "config": {
        "model_name": params["agent"]["model_name"],
        "use_tool_calling": bool(params["agent"]["use_tool_calling"]),
        "top_k": int(params["retrieval"]["top_k"]),
        "min_score": float(params["retrieval"]["min_score"]),
        "ambiguity_margin": float(params["retrieval"]["ambiguity_margin"]),
    },
}
metrics_path.write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
