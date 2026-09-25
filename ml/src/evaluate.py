"""Evaluates the fine-tuned text2sql model against the held-out test split and writes
ml/metrics.json (a DVC metrics file — see `dvc metrics show` / `dvc metrics diff`).

Reports:
  - exact_match: fraction of predictions that exactly match the reference SQL (post-whitespace-normalize)
  - valid_sql_rate: fraction of predictions that parse as a safe, read-only SQL statement
    (mirrors the read-only/no-multi-statement checks in backend/app/services/sql_validator.py,
    reimplemented minimally here so this pipeline doesn't depend on importing the backend app)
"""
import json
from pathlib import Path

import sqlglot
import torch
from sqlglot import exp
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "ml" / "data"
MODEL_DIR = REPO_ROOT / "ml" / "models" / "text2sql"
METRICS_PATH = REPO_ROOT / "ml" / "metrics.json"
PREDICTIONS_PATH = REPO_ROOT / "ml" / "predictions.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_safe_readonly_sql(sql: str) -> bool:
    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
    except Exception:
        return False
    if len(statements) != 1:
        return False
    tree = statements[0]
    return isinstance(tree, (exp.Select, exp.Union, exp.With))


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(MODEL_DIR))
    model.eval()

    test_records = load_jsonl(DATA_DIR / "test.jsonl")

    predictions = []
    with torch.no_grad():
        for record in test_records:
            inputs = tokenizer(record["input"], return_tensors="pt", truncation=True, max_length=160)
            output_ids = model.generate(**inputs, max_new_tokens=96)
            predicted_sql = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            predictions.append(
                {"question": record["question"], "reference_sql": record["sql"], "predicted_sql": predicted_sql}
            )

    n = len(predictions)
    exact_matches = sum(
        1 for p in predictions if p["predicted_sql"].strip() == p["reference_sql"].strip()
    )
    valid_sql = sum(1 for p in predictions if is_safe_readonly_sql(p["predicted_sql"]))

    metrics = {
        "n_test": n,
        "exact_match": round(exact_matches / n, 4) if n else 0.0,
        "valid_sql_rate": round(valid_sql / n, 4) if n else 0.0,
    }

    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    with PREDICTIONS_PATH.open("w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p) + "\n")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
