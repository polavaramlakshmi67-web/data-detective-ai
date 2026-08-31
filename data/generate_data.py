from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# NOVAMART DATA GENERATOR
# ============================================================

np.random.seed(42)

DATA_DIR = Path(__file__).resolve().parent
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. CUSTOMERS
# ============================================================

n_customers = 500

customers = pd.DataFrame(
    {
        "customer_id": [f"C{i:04d}" for i in range(1, n_customers + 1)],
        "customer_name": [
            f"Customer {i}" for i in range(1, n_customers + 1)
        ],
        "region": np.random.choice(
            ["North", "South", "East", "West"],
            size=n_customers,
            p=[0.25, 0.25, 0.20, 0.30],
        ),
        "customer_segment": np.random.choice(
            ["Consumer", "Corporate", "Home Office"],
            size=n_customers,
            p=[0.60, 0.25, 0.15],
        ),
    }
)

customers.to_csv(DATA_DIR / "customers.csv", index=False)


# ============================================================
# 2. PRODUCTS
# ============================================================

product_names = [
    "Laptop",
    "Monitor",
    "Keyboard",
    "Mouse",
    "Headphones",
    "Webcam",
    "Printer",
    "Tablet",
    "Smartphone",
    "Desk",
    "Chair",
    "USB Hub",
    "SSD",
    "Router",
    "Speaker",
    "Power Bank",
    "Smartwatch",
    "Camera",
    "Microphone",
    "Backpack",
]

categories = [
    "Electronics",
    "Electronics",
    "Accessories",
    "Accessories",
    "Accessories",
    "Electronics",
    "Office",
    "Electronics",
    "Electronics",
    "Furniture",
    "Furniture",
    "Accessories",
    "Electronics",
    "Electronics",
    "Electronics",
    "Accessories",
    "Electronics",
    "Electronics",
    "Accessories",
    "Accessories",
]

products = pd.DataFrame(
    {
        "product_id": [f"P{i:03d}" for i in range(1, 21)],
        "product_name": product_names,
        "category": categories,
        "price": np.random.randint(20, 1200, size=20).astype(float),
    }
)

products.to_csv(DATA_DIR / "products.csv", index=False)


# ============================================================
# 3. SALES
# ============================================================

dates = pd.date_range(
    start="2025-01-01",
    end="2026-06-30",
    freq="D",
)

n_sales = 12000

sales = pd.DataFrame(
    {
        "order_id": [
            f"O{i:06d}" for i in range(1, n_sales + 1)
        ],
        "order_date": pd.to_datetime(
            np.random.choice(dates, size=n_sales)
        ),
        "customer_id": np.random.choice(
            customers["customer_id"].to_numpy(),
            size=n_sales,
        ),
        "product_id": np.random.choice(
            products["product_id"].to_numpy(),
            size=n_sales,
        ),
        "quantity": np.random.randint(
            1, 5, size=n_sales
        ).astype(np.int64),
    }
)


# Add product price

sales = sales.merge(
    products[["product_id", "price"]],
    on="product_id",
    how="left",
)


# Add customer region

sales = sales.merge(
    customers[["customer_id", "region"]],
    on="customer_id",
    how="left",
)


# ============================================================
# BUSINESS PROBLEM
# ============================================================
# Starting March 2026:
# West region + P001/P002/P003 experience a sales decline.
# This gives our AI something meaningful to investigate.


problem_mask = (
    (sales["order_date"] >= pd.Timestamp("2026-03-01"))
    & (sales["region"] == "West")
    & (sales["product_id"].isin(["P001", "P002", "P003"]))
)


# Convert affected values safely

affected_quantity = (
    sales.loc[problem_mask, "quantity"]
    .to_numpy(dtype=np.int64)
)


affected_quantity = np.maximum(
    1,
    np.rint(affected_quantity * 0.45),
).astype(np.int64)


sales.loc[problem_mask, "quantity"] = affected_quantity


# Calculate revenue

sales["revenue"] = (
    sales["quantity"].astype(float)
    * sales["price"].astype(float)
)


# Round revenue

sales["revenue"] = sales["revenue"].round(2)


# Save

sales.to_csv(DATA_DIR / "sales.csv", index=False)


# ============================================================
# 4. INVENTORY
# ============================================================

inventory_rows = []

months = pd.date_range(
    start="2025-01-01",
    end="2026-06-01",
    freq="MS",
)

problem_products = ["P001", "P002", "P003"]

for month in months:

    for product_id in products["product_id"]:

        stock = int(np.random.randint(50, 500))

        # Create inventory problem from March 2026

        if (
            month >= pd.Timestamp("2026-03-01")
            and product_id in problem_products
        ):
            stock = int(np.random.randint(5, 50))

        inventory_rows.append(
            [
                month,
                product_id,
                stock,
            ]
        )


inventory = pd.DataFrame(
    inventory_rows,
    columns=[
        "month",
        "product_id",
        "stock_quantity",
    ],
)

inventory["stock_quantity"] = inventory[
    "stock_quantity"
].astype(np.int64)

inventory.to_csv(
    DATA_DIR / "inventory.csv",
    index=False,
)


# ============================================================
# 5. MARKETING
# ============================================================

marketing_rows = []

regions = [
    "North",
    "South",
    "East",
    "West",
]

for month in months:

    for region in regions:

        marketing_rows.append(
            [
                month,
                region,
                int(np.random.randint(10000, 50000)),
                int(np.random.randint(500, 5000)),
                int(np.random.randint(50, 500)),
            ]
        )


marketing = pd.DataFrame(
    marketing_rows,
    columns=[
        "month",
        "region",
        "marketing_spend",
        "impressions",
        "campaign_clicks",
    ],
)

marketing.to_csv(
    DATA_DIR / "marketing.csv",
    index=False,
)


# ============================================================
# 6. CUSTOMER SUPPORT
# ============================================================

support_rows = []

support_issues = [
    "Delivery Delay",
    "Product Issue",
    "Payment Problem",
    "Out of Stock",
    "Refund Request",
]

for i in range(3000):

    ticket_date = pd.Timestamp(
        np.random.choice(dates)
    )

    region = np.random.choice(regions)

    # More stock-related complaints
    # in the affected West region.

    if (
        ticket_date >= pd.Timestamp("2026-03-01")
        and region == "West"
    ):

        issue_type = np.random.choice(
            [
                "Out of Stock",
                "Delivery Delay",
                "Product Issue",
            ]
        )

    else:

        issue_type = np.random.choice(
            support_issues
        )

    support_rows.append(
        [
            f"T{i:05d}",
            ticket_date,
            region,
            issue_type,
        ]
    )


support = pd.DataFrame(
    support_rows,
    columns=[
        "ticket_id",
        "ticket_date",
        "region",
        "issue_type",
    ],
)

support.to_csv(
    DATA_DIR / "support.csv",
    index=False,
)


# ============================================================
# VALIDATION
# ============================================================

files = [
    "sales.csv",
    "customers.csv",
    "products.csv",
    "inventory.csv",
    "marketing.csv",
    "support.csv",
]

print()
print("=" * 55)
print("NOVAMART DATASET CREATED SUCCESSFULLY")
print("=" * 55)

for filename in files:

    filepath = DATA_DIR / filename

    dataframe = pd.read_csv(filepath)

    print(
        f"{filename:<20} {len(dataframe):>8,} rows"
    )

print("=" * 55)
print("All datasets are ready for Data Detective AI.")
print("=" * 55) 