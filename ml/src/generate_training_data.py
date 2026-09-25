"""Builds a templated (question, SQL) dataset for fine-tuning a text-to-SQL model on the `sales`
schema. Templates are combined with real dimension values read from the current
backend/data/superstore.csv, so the training set tracks whatever dataset DVC currently has
checked out — if the underlying data changes (new regions, categories, etc.), `dvc repro`
regenerates training examples that reflect it, rather than a frozen, hand-written example list.

Usage: python ml/src/generate_training_data.py (run from the repo root, or anywhere — paths below
are resolved relative to this file).
"""
import json
import random
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "backend" / "data" / "superstore.csv"
PARAMS_PATH = REPO_ROOT / "params.yaml"
OUT_DIR = REPO_ROOT / "ml" / "data"

SCHEMA_PREFIX = (
    "Translate to PostgreSQL. Schema: sales(order_date date, category text, sub_category text, "
    "region text, state text, city text, product_name text, customer_name text, sales numeric, "
    "quantity integer, discount numeric, profit numeric). Question: "
)

# metric key -> (display phrase, column, aggregate fn, output alias)
METRICS = {
    "revenue": ("revenue", "sales", "SUM", "total_sales"),
    "sales": ("sales", "sales", "SUM", "total_sales"),
    "profit": ("profit", "profit", "SUM", "total_profit"),
    "quantity": ("units sold", "quantity", "SUM", "total_quantity"),
    "discount": ("discount", "discount", "AVG", "avg_discount"),
}

# dimension column -> (singular phrase, plural phrase)
DIMENSIONS = {
    "category": ("category", "categories"),
    "sub_category": ("sub-category", "sub-categories"),
    "region": ("region", "regions"),
    "state": ("state", "states"),
    "city": ("city", "cities"),
    "product_name": ("product", "products"),
    "customer_name": ("customer", "customers"),
}

YEARS = [2023, 2024, 2025]
TOP_N = [3, 5, 10]


def load_dimension_values(df: pd.DataFrame) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for col in ("region", "state", "category", "sub_category", "city"):
        values[col] = sorted(v for v in df[col].dropna().unique().tolist())
    return values


def esc(value: str) -> str:
    return value.replace("'", "''")


def gen_examples(dim_values: dict[str, list[str]], rng: random.Random) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []

    def add(question: str, sql: str) -> None:
        examples.append({"question": question, "sql": " ".join(sql.split())})

    for metric_key, (metric_phrase, col, agg, alias) in METRICS.items():
        for dim, (dim_singular, dim_plural) in DIMENSIONS.items():
            # 1. total metric by dimension
            add(
                f"What is the total {metric_phrase} by {dim_singular}?",
                f"SELECT {dim}, {agg}({col}) AS {alias} FROM sales GROUP BY {dim} ORDER BY {alias} DESC",
            )
            # 2. highest single dimension value
            add(
                f"Which {dim_singular} had the highest {metric_phrase}?",
                f"SELECT {dim}, {agg}({col}) AS {alias} FROM sales GROUP BY {dim} ORDER BY {alias} DESC LIMIT 1",
            )
            # 3. average metric by dimension (skip when metric itself is already an average)
            if agg == "SUM":
                add(
                    f"What is the average {metric_phrase} by {dim_singular}?",
                    f"SELECT {dim}, AVG({col}) AS avg_{col} FROM sales GROUP BY {dim} ORDER BY avg_{col} DESC",
                )
            # 4. top-N by dimension
            for n in TOP_N:
                add(
                    f"Show the top {n} {dim_plural} by {metric_phrase}.",
                    f"SELECT {dim}, {agg}({col}) AS {alias} FROM sales GROUP BY {dim} "
                    f"ORDER BY {alias} DESC LIMIT {n}",
                )
            # 5. top-N by dimension, filtered to a year
            for year in YEARS:
                n = rng.choice(TOP_N)
                add(
                    f"Show the top {n} {dim_plural} by {metric_phrase} in {year}.",
                    f"SELECT {dim}, {agg}({col}) AS {alias} FROM sales "
                    f"WHERE order_date >= '{year}-01-01' AND order_date < '{year + 1}-01-01' "
                    f"GROUP BY {dim} ORDER BY {alias} DESC LIMIT {n}",
                )
            # 6. filtered to a specific real value of a low-cardinality dimension
            if dim in dim_values and dim_values[dim]:
                value = rng.choice(dim_values[dim])
                add(
                    f"What was the total {metric_phrase} for {dim_singular} '{value}'?",
                    f"SELECT {agg}({col}) AS {alias} FROM sales WHERE {dim} = '{esc(value)}'",
                )

        # 7. monthly trend for a metric, per year
        for year in YEARS:
            add(
                f"Show monthly {metric_phrase} for {year}.",
                f"SELECT date_trunc('month', order_date) AS month, {agg}({col}) AS {alias} FROM sales "
                f"WHERE order_date >= '{year}-01-01' AND order_date < '{year + 1}-01-01' "
                f"GROUP BY month ORDER BY month",
            )

    # 8. compare two metrics by dimension
    metric_keys = list(METRICS.keys())
    for dim, (dim_singular, _) in DIMENSIONS.items():
        for i, m1 in enumerate(metric_keys):
            for m2 in metric_keys[i + 1 :]:
                p1, c1, a1, alias1 = METRICS[m1]
                p2, c2, a2, alias2 = METRICS[m2]
                add(
                    f"Compare {p1} and {p2} by {dim_singular}.",
                    f"SELECT {dim}, {a1}({c1}) AS {alias1}, {a2}({c2}) AS {alias2} FROM sales "
                    f"GROUP BY {dim} ORDER BY {alias1} DESC",
                )

    return examples


def main() -> None:
    params = yaml.safe_load(PARAMS_PATH.read_text())["generate_data"]
    rng = random.Random(params["seed"])

    df = pd.read_csv(CSV_PATH)
    dim_values = load_dimension_values(df)

    examples = gen_examples(dim_values, rng)
    # de-dupe identical questions (a couple of templates can coincide for metric=="sales" vs "revenue")
    seen: set[str] = set()
    unique = []
    for ex in examples:
        if ex["question"] not in seen:
            seen.add(ex["question"])
            unique.append(ex)

    rng.shuffle(unique)
    unique = unique[: params["max_examples"]]

    n = len(unique)
    n_val = max(1, int(n * params["val_fraction"]))
    n_test = max(1, int(n * params["test_fraction"]))
    n_train = n - n_val - n_test

    train, val, test = unique[:n_train], unique[n_train : n_train + n_val], unique[n_train + n_val :]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, split in (("train", train), ("val", val), ("test", test)):
        path = OUT_DIR / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for ex in split:
                record = {"input": SCHEMA_PREFIX + ex["question"], "question": ex["question"], "sql": ex["sql"]}
                f.write(json.dumps(record) + "\n")
        print(f"{name}: {len(split)} examples -> {path}")


if __name__ == "__main__":
    main()
