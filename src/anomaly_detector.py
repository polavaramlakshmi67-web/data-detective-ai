from pathlib import Path

import pandas as pd


def detect_sales_anomalies(
    data_folder,
):
    """
    Detect unusual monthly revenue changes
    by region.
    """

    data_folder = Path(data_folder)

    sales = pd.read_csv(
        data_folder / "sales.csv"
    )

    sales["order_date"] = pd.to_datetime(
        sales["order_date"],
        errors="coerce",
    )

    sales = sales.dropna(
        subset=["order_date"]
    )

    sales["month"] = (
        sales["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_region = (
        sales
        .groupby(
            ["month", "region"],
            as_index=False,
        )["revenue"]
        .sum()
    )

    monthly_region = (
        monthly_region
        .sort_values(
            ["region", "month"]
        )
    )

    monthly_region[
        "previous_revenue"
    ] = (
        monthly_region
        .groupby("region")[
            "revenue"
        ]
        .shift(1)
    )

    monthly_region[
        "revenue_change_pct"
    ] = (
        (
            monthly_region["revenue"]
            - monthly_region[
                "previous_revenue"
            ]
        )
        / monthly_region[
            "previous_revenue"
        ]
        * 100
    )

    anomalies = monthly_region[
        monthly_region[
            "revenue_change_pct"
        ] <= -20
    ].copy()

    anomalies = anomalies.sort_values(
        "revenue_change_pct"
    )

    return anomalies


def detect_product_anomalies(
    data_folder,
):
    """
    Detect unusual monthly revenue changes
    by product.
    """

    data_folder = Path(data_folder)

    sales = pd.read_csv(
        data_folder / "sales.csv"
    )

    products = pd.read_csv(
        data_folder / "products.csv"
    )

    sales["order_date"] = pd.to_datetime(
        sales["order_date"],
        errors="coerce",
    )

    sales = sales.dropna(
        subset=["order_date"]
    )

    sales["month"] = (
        sales["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_product = (
        sales
        .groupby(
            ["month", "product_id"],
            as_index=False,
        )["revenue"]
        .sum()
    )

    monthly_product = (
        monthly_product
        .sort_values(
            ["product_id", "month"]
        )
    )

    monthly_product[
        "previous_revenue"
    ] = (
        monthly_product
        .groupby("product_id")[
            "revenue"
        ]
        .shift(1)
    )

    monthly_product[
        "revenue_change_pct"
    ] = (
        (
            monthly_product["revenue"]
            - monthly_product[
                "previous_revenue"
            ]
        )
        / monthly_product[
            "previous_revenue"
        ]
        * 100
    )

    anomalies = monthly_product[
        monthly_product[
            "revenue_change_pct"
        ] <= -30
    ].copy()

    anomalies = anomalies.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
            ]
        ],
        on="product_id",
        how="left",
    )

    anomalies = anomalies.sort_values(
        "revenue_change_pct"
    )

    return anomalies


def print_region_anomalies(
    anomalies,
):

    print()
    print("=" * 70)
    print(
        "REGIONAL REVENUE ANOMALIES"
    )
    print("=" * 70)

    if anomalies.empty:

        print(
            "No significant regional "
            "anomalies found."
        )

        return

    for _, row in anomalies.head(
        15
    ).iterrows():

        print(
            f"{row['month']} | "
            f"{row['region']:<10} | "
            f"Revenue: ₹"
            f"{row['revenue']:,.0f} | "
            f"Change: "
            f"{row['revenue_change_pct']:.1f}%"
        )


def print_product_anomalies(
    anomalies,
):

    print()
    print("=" * 70)
    print(
        "PRODUCT REVENUE ANOMALIES"
    )
    print("=" * 70)

    if anomalies.empty:

        print(
            "No significant product "
            "anomalies found."
        )

        return

    for _, row in anomalies.head(
        15
    ).iterrows():

        print(
            f"{row['month']} | "
            f"{row['product_id']} "
            f"{row['product_name']:<15} | "
            f"Change: "
            f"{row['revenue_change_pct']:.1f}%"
        )


if __name__ == "__main__":

    project_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    data_folder = (
        project_root / "data"
    )

    region_anomalies = (
        detect_sales_anomalies(
            data_folder
        )
    )

    product_anomalies = (
        detect_product_anomalies(
            data_folder
        )
    )

    print_region_anomalies(
        region_anomalies
    )

    print_product_anomalies(
        product_anomalies
    )

    print()
    print(
        "Anomaly investigation "
        "complete."
    )