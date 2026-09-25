"""Generates a realistic Superstore-style sales CSV for local/dev seeding.

Run standalone: `python data/generate_dataset.py` (writes data/superstore.csv).
Deterministic (fixed seed) so re-running produces the same dataset for reproducible demos.
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

REGIONS_STATES_CITIES = {
    "West": {
        "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
        "Washington": ["Seattle", "Spokane"],
        "Oregon": ["Portland", "Eugene"],
        "Arizona": ["Phoenix", "Tucson"],
    },
    "East": {
        "New York": ["New York City", "Buffalo", "Albany"],
        "Massachusetts": ["Boston", "Worcester"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh"],
        "New Jersey": ["Newark", "Jersey City"],
    },
    "Central": {
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
        "Illinois": ["Chicago", "Springfield"],
        "Ohio": ["Columbus", "Cleveland"],
        "Michigan": ["Detroit", "Ann Arbor"],
    },
    "South": {
        "Florida": ["Miami", "Orlando", "Tampa"],
        "Georgia": ["Atlanta", "Savannah"],
        "North Carolina": ["Charlotte", "Raleigh"],
        "Tennessee": ["Nashville", "Memphis"],
    },
}

CATEGORY_PRODUCTS = {
    "Technology": {
        "Phones": ["Apple iPhone 15", "Samsung Galaxy S24", "Google Pixel 9", "OnePlus 12"],
        "Computers": ["Dell XPS 15", "MacBook Pro 14", "Lenovo ThinkPad X1", "HP Spectre x360"],
        "Accessories": ["Logitech MX Master 3", "Anker USB-C Hub", "Sony WH-1000XM5", "Kensington Laptop Stand"],
        "Copiers": ["Canon imageCLASS MF445dw", "HP LaserJet Pro M404", "Brother HL-L2350DW"],
    },
    "Furniture": {
        "Chairs": ["Herman Miller Aeron", "Steelcase Leap", "Autonomous ErgoChair Pro", "IKEA Markus"],
        "Tables": ["Standing Desk Pro", "Glass Conference Table", "IKEA Bekant Desk"],
        "Bookcases": ["Sauder 5-Shelf Bookcase", "Modern Ladder Bookshelf"],
        "Storage": ["Metal Filing Cabinet", "Rolling Storage Cart"],
    },
    "Office Supplies": {
        "Paper": ["Xerox Premium Copy Paper", "Hammermill Color Copy Paper"],
        "Binders": ["Avery Heavy-Duty Binder", "Wilson Jones Round-Ring Binder"],
        "Art": ["Sharpie Marker Set", "Crayola Colored Pencils", "Post-it Notes Bulk Pack"],
        "Labels": ["Avery Address Labels", "DYMO LabelWriter Labels"],
        "Storage": ["Sterilite Storage Bin", "Bankers Box Stor/File"],
    },
}

CUSTOMER_FIRST = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Quinn", "Peyton",
                  "Cameron", "Drew", "Sam", "Reese", "Skyler", "Hayden", "Rowan", "Emerson", "Dakota", "Finley"]
CUSTOMER_LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                  "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee"]

NUM_ROWS = 6000
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def build_customers(n: int) -> list[tuple[str, str]]:
    customers = []
    for i in range(1, n + 1):
        name = f"{random.choice(CUSTOMER_FIRST)} {random.choice(CUSTOMER_LAST)}"
        customers.append((f"CUST-{i:04d}", name))
    return customers


def main() -> None:
    customers = build_customers(400)
    rows = []

    flat_products = []
    for category, subcats in CATEGORY_PRODUCTS.items():
        for sub_category, products in subcats.items():
            for product_name in products:
                flat_products.append((category, sub_category, product_name))

    product_ids = {name: f"PROD-{i:04d}" for i, (_, _, name) in enumerate(flat_products, start=1)}

    for i in range(1, NUM_ROWS + 1):
        region = random.choice(list(REGIONS_STATES_CITIES.keys()))
        state = random.choice(list(REGIONS_STATES_CITIES[region].keys()))
        city = random.choice(REGIONS_STATES_CITIES[region][state])

        category, sub_category, product_name = random.choice(flat_products)
        customer_id, customer_name = random.choice(customers)

        order_date = random_date(START_DATE, END_DATE)
        # Slight seasonal + year-over-year growth bump so charts show a real trend.
        seasonal = 1.0 + (0.35 if order_date.month in (11, 12) else 0.0)
        yoy_growth = 1.0 + (order_date.year - START_DATE.year) * 0.12

        base_price = {
            "Technology": random.uniform(80, 1800),
            "Furniture": random.uniform(60, 900),
            "Office Supplies": random.uniform(5, 120),
        }[category]

        quantity = random.randint(1, 8)
        discount = round(random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3]), 2)
        sales = round(base_price * quantity * seasonal * yoy_growth, 2)
        margin = random.uniform(0.05, 0.35) - (discount * 0.6)
        profit = round(sales * margin, 2)

        rows.append(
            {
                "order_id": f"ORD-{100000 + i}",
                "order_date": order_date.isoformat(),
                "customer_id": customer_id,
                "customer_name": customer_name,
                "country": "United States",
                "city": city,
                "state": state,
                "region": region,
                "product_id": product_ids[product_name],
                "product_name": product_name,
                "category": category,
                "sub_category": sub_category,
                "sales": sales,
                "quantity": quantity,
                "discount": discount,
                "profit": profit,
            }
        )

    df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
    out_path = Path(__file__).parent / "superstore.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
