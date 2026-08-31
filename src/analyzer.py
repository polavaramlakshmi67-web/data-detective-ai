from pathlib import Path

import pandas as pd


def load_data(data_folder):
    """Load all NovaMart datasets."""

    data_folder = Path(data_folder)

    sales = pd.read_csv(data_folder / "sales.csv")
    inventory = pd.read_csv(data_folder / "inventory.csv")
    support = pd.read_csv(data_folder / "support.csv")
    marketing = pd.read_csv(data_folder / "marketing.csv")

    sales["order_date"] = pd.to_datetime(
        sales["order_date"]
    )

    inventory["month"] = pd.to_datetime(
        inventory["month"]
    )

    support["ticket_date"] = pd.to_datetime(
        support["ticket_date"]
    )

    marketing["month"] = pd.to_datetime(
        marketing["month"]
    )

    return (
        sales,
        inventory,
        support,
        marketing,
    )


def investigate_west_region(data_folder):
    """
    Investigate the intentional West-region
    business problem.
    """

    (
        sales,
        inventory,
        support,
        marketing,
    ) = load_data(data_folder)

    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    sales["month"] = (
        sales["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    west_sales = sales[
        sales["region"] == "West"
    ].copy()

    monthly_sales = (
        west_sales
        .groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            quantity=("quantity", "sum"),
        )
    )

    monthly_sales["previous_revenue"] = (
        monthly_sales["revenue"].shift(1)
    )

    monthly_sales["revenue_change_pct"] = (
        (
            monthly_sales["revenue"]
            - monthly_sales["previous_revenue"]
        )
        / monthly_sales["previous_revenue"]
        * 100
    )

    # --------------------------------------------------------
    # INVENTORY
    # --------------------------------------------------------

    problem_products = [
        "P001",
        "P002",
        "P003",
    ]

    problem_inventory = inventory[
        inventory["product_id"].isin(
            problem_products
        )
    ].copy()

    inventory_monthly = (
        problem_inventory
        .groupby("month", as_index=False)
        ["stock_quantity"]
        .mean()
    )

    inventory_monthly["month"] = (
        inventory_monthly["month"]
        .dt.to_period("M")
        .astype(str)
    )

    # --------------------------------------------------------
    # SUPPORT
    # --------------------------------------------------------

    west_support = support[
        support["region"] == "West"
    ].copy()

    west_support["month"] = (
        west_support["ticket_date"]
        .dt.to_period("M")
        .astype(str)
    )

    support_monthly = (
        west_support[
            west_support["issue_type"]
            == "Out of Stock"
        ]
        .groupby("month")
        .size()
        .reset_index(
            name="out_of_stock_tickets"
        )
    )

    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    west_marketing = marketing[
        marketing["region"] == "West"
    ].copy()

    west_marketing["month"] = (
        west_marketing["month"]
        .dt.to_period("M")
        .astype(str)
    )

    marketing_monthly = (
        west_marketing[
            [
                "month",
                "marketing_spend",
                "campaign_clicks",
            ]
        ]
    )

    # --------------------------------------------------------
    # COMBINE EVIDENCE
    # --------------------------------------------------------

    investigation = monthly_sales.merge(
        inventory_monthly,
        on="month",
        how="left",
    )

    investigation = investigation.merge(
        support_monthly,
        on="month",
        how="left",
    )

    investigation = investigation.merge(
        marketing_monthly,
        on="month",
        how="left",
    )

    investigation[
        "out_of_stock_tickets"
    ] = investigation[
        "out_of_stock_tickets"
    ].fillna(0)

    # --------------------------------------------------------
    # FOCUS ON 2026
    # --------------------------------------------------------

    investigation["month_date"] = pd.to_datetime(
        investigation["month"]
    )

    investigation_2026 = investigation[
        investigation["month_date"]
        >= pd.Timestamp("2026-01-01")
    ].copy()

    return investigation_2026


def print_investigation(df):

    print()
    print("=" * 80)
    print("DATA DETECTIVE — WEST REGION INVESTIGATION")
    print("=" * 80)

    for _, row in df.iterrows():

        print(
            f"\nMonth: {row['month']}"
        )

        print(
            f"Revenue: ${row['revenue']:,.0f}"
        )

        if pd.notna(
            row["revenue_change_pct"]
        ):

            print(
                f"Revenue change: "
                f"{row['revenue_change_pct']:.1f}%"
            )

        print(
            f"Average problem-product stock: "
            f"{row['stock_quantity']:.0f}"
        )

        print(
            f"Out-of-stock tickets: "
            f"{row['out_of_stock_tickets']:.0f}"
        )

        print(
            f"Marketing spend: "
            f"${row['marketing_spend']:,.0f}"
        )

        print(
            f"Campaign clicks: "
            f"{row['campaign_clicks']:,.0f}"
        )


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[1]

    data_folder = project_root / "data"

    result = investigate_west_region(
        data_folder
    )

    print_investigation(result)

    print()
    print("=" * 80)
    print("Investigation complete.")
    print("=" * 80)