"""Creates tables and loads the Superstore CSV into the `sales` table.

Usage: `python -m app.database.seed` (from the backend/ directory, with .env configured).
Idempotent: truncates `sales` before loading so re-running never duplicates rows.
"""
import os
import sys
from pathlib import Path

import pandas as pd

from app.database.connection import engine, session_scope
from app.database.models import Base, Sale

CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "superstore.csv"

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_name", "country", "city", "state",
    "region", "product_id", "product_name", "category", "sub_category", "sales", "quantity",
    "discount", "profit",
]


def create_tables() -> None:
    Base.metadata.create_all(engine)
    print("Tables ensured (users, sales, query_history, conversation_messages).")


def load_csv(csv_path: Path = CSV_PATH, force: bool | None = None) -> None:
    force = force if force is not None else os.getenv("FORCE_RESEED", "").lower() in ("1", "true", "yes")

    with session_scope() as db:
        existing = db.query(Sale).count()
    if existing and not force:
        print(f"sales table already has {existing} rows; skipping seed (set FORCE_RESEED=1 to reload).")
        return

    if not csv_path.exists():
        print(f"CSV not found at {csv_path}. Run `python data/generate_dataset.py` first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path, parse_dates=["order_date"])
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        print(f"CSV is missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    df = df[REQUIRED_COLUMNS]
    df["order_date"] = df["order_date"].dt.date
    records = df.to_dict(orient="records")

    with session_scope() as db:
        db.query(Sale).delete()
        db.bulk_insert_mappings(Sale, records)

    print(f"Loaded {len(records)} rows into sales.")


def main() -> None:
    create_tables()
    load_csv()


if __name__ == "__main__":
    main()
