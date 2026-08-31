from pathlib import Path

import pandas as pd


def load_data(data_folder):

    data_folder = Path(
        data_folder
    )

    sales = pd.read_csv(
        data_folder / "sales.csv"
    )

    inventory = pd.read_csv(
        data_folder / "inventory.csv"
    )

    support = pd.read_csv(
        data_folder / "support.csv"
    )

    marketing = pd.read_csv(
        data_folder / "marketing.csv"
    )

    sales["order_date"] = pd.to_datetime(
        sales["order_date"],
        errors="coerce",
    )

    inventory["month"] = pd.to_datetime(
        inventory["month"],
        errors="coerce",
    )

    support["ticket_date"] = pd.to_datetime(
        support["ticket_date"],
        errors="coerce",
    )

    marketing["month"] = pd.to_datetime(
        marketing["month"],
        errors="coerce",
    )

    return (
        sales,
        inventory,
        support,
        marketing,
    )


def calculate_evidence(
    data_folder,
):

    (
        sales,
        inventory,
        support,
        marketing,
    ) = load_data(data_folder)

    # ========================================================
    # WEST SALES
    # ========================================================

    west_sales = sales[
        sales["region"] == "West"
    ].copy()

    west_sales["month"] = (
        west_sales["order_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_sales = (
        west_sales
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            revenue=("revenue", "sum"),
            orders=(
                "order_id",
                "nunique",
            ),
        )
        .sort_values("month")
    )

    monthly_sales[
        "previous_revenue"
    ] = (
        monthly_sales[
            "revenue"
        ].shift(1)
    )

    monthly_sales[
        "revenue_change_pct"
    ] = (
        (
            monthly_sales["revenue"]
            - monthly_sales[
                "previous_revenue"
            ]
        )
        / monthly_sales[
            "previous_revenue"
        ]
        * 100
    )

    # ========================================================
    # INVENTORY
    # ========================================================

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
        .groupby(
            "month",
            as_index=False,
        )["stock_quantity"]
        .mean()
    )

    # ========================================================
    # SUPPORT
    # ========================================================

    west_support = support[
        support["region"] == "West"
    ].copy()

    west_support["month"] = (
        west_support["ticket_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    stock_tickets = (
        west_support[
            west_support[
                "issue_type"
            ]
            == "Out of Stock"
        ]
        .groupby("month")
        .size()
        .reset_index(
            name="out_of_stock_tickets"
        )
    )

    # ========================================================
    # MARKETING
    # ========================================================

    west_marketing = marketing[
        marketing["region"] == "West"
    ][
        [
            "month",
            "marketing_spend",
            "campaign_clicks",
        ]
    ].copy()

    # ========================================================
    # COMBINE
    # ========================================================

    evidence = monthly_sales.merge(
        inventory_monthly,
        on="month",
        how="left",
    )

    evidence = evidence.merge(
        stock_tickets,
        on="month",
        how="left",
    )

    evidence = evidence.merge(
        west_marketing,
        on="month",
        how="left",
    )

    evidence[
        "out_of_stock_tickets"
    ] = evidence[
        "out_of_stock_tickets"
    ].fillna(0)

    return evidence


def investigate(evidence):

    investigation_period = evidence[
        evidence["month"]
        >= pd.Timestamp(
            "2026-03-01"
        )
    ].copy()

    before_period = evidence[
        (
            evidence["month"]
            >= pd.Timestamp(
                "2026-01-01"
            )
        )
        & (
            evidence["month"]
            < pd.Timestamp(
                "2026-03-01"
            )
        )
    ].copy()

    results = {}

    # ========================================================
    # INVENTORY
    # ========================================================

    avg_problem_stock = (
        investigation_period[
            "stock_quantity"
        ].mean()
    )

    avg_before_stock = (
        before_period[
            "stock_quantity"
        ].mean()
    )

    if (
        pd.notna(avg_before_stock)
        and avg_before_stock != 0
    ):

        stock_change = (
            (
                avg_problem_stock
                - avg_before_stock
            )
            / avg_before_stock
            * 100
        )

    else:

        stock_change = 0

    inventory_score = min(
        100,
        max(0, -stock_change),
    )

    results["inventory"] = {
        "score": round(
            inventory_score,
            1,
        ),
        "before_average_stock": round(
            avg_before_stock,
            1,
        ),
        "problem_average_stock": round(
            avg_problem_stock,
            1,
        ),
        "change_percent": round(
            stock_change,
            1,
        ),
    }

    # ========================================================
    # SUPPORT
    # ========================================================

    avg_tickets = (
        investigation_period[
            "out_of_stock_tickets"
        ].mean()
    )

    before_tickets = (
        before_period[
            "out_of_stock_tickets"
        ].mean()
    )

    if (
        pd.notna(before_tickets)
        and before_tickets != 0
    ):

        ticket_change = (
            (
                avg_tickets
                - before_tickets
            )
            / before_tickets
            * 100
        )

    else:

        ticket_change = 0

    support_score = min(
        100,
        max(0, ticket_change),
    )

    results["support"] = {
        "score": round(
            support_score,
            1,
        ),
        "before_average_tickets": round(
            before_tickets,
            1,
        ),
        "problem_average_tickets": round(
            avg_tickets,
            1,
        ),
        "change_percent": round(
            ticket_change,
            1,
        ),
    }

    # ========================================================
    # MARKETING
    # ========================================================

    avg_clicks = (
        investigation_period[
            "campaign_clicks"
        ].mean()
    )

    before_clicks = (
        before_period[
            "campaign_clicks"
        ].mean()
    )

    if (
        pd.notna(before_clicks)
        and before_clicks != 0
    ):

        click_change = (
            (
                avg_clicks
                - before_clicks
            )
            / before_clicks
            * 100
        )

    else:

        click_change = 0

    marketing_score = min(
        100,
        max(0, -click_change),
    )

    results["marketing"] = {
        "score": round(
            marketing_score,
            1,
        ),
        "before_average_clicks": round(
            before_clicks,
            1,
        ),
        "problem_average_clicks": round(
            avg_clicks,
            1,
        ),
        "change_percent": round(
            click_change,
            1,
        ),
    }

    return results


def generate_explanation(
    results,
):

    ranked = sorted(
        results.items(),
        key=lambda item: item[1][
            "score"
        ],
        reverse=True,
    )

    strongest_cause = ranked[0]

    cause_name = strongest_cause[0]

    cause_data = strongest_cause[1]

    explanations = {

        "inventory": (
            "Inventory is the strongest "
            "evidence signal. The average "
            "stock level for the investigated "
            "products declined during the "
            "problem period."
        ),

        "support": (
            "Customer support is the strongest "
            "evidence signal. Out-of-stock "
            "complaints increased during the "
            "investigation period."
        ),

        "marketing": (
            "Marketing is the strongest "
            "evidence signal because campaign "
            "engagement declined during the "
            "investigation period."
        ),
    }

    explanation = explanations[
        cause_name
    ]

    return {
        "strongest_signal": cause_name,
        "score": cause_data["score"],
        "explanation": explanation,
        "ranking": [
            {
                "cause": cause,
                "score": data[
                    "score"
                ],
            }
            for cause, data in ranked
        ],
    }


def print_report(
    results,
    conclusion,
):

    print()
    print("=" * 70)
    print(
        "DATA DETECTIVE — "
        "AI INVESTIGATION"
    )
    print("=" * 70)

    print()
    print("EVIDENCE RANKING")
    print("-" * 70)

    for item in conclusion[
        "ranking"
    ]:

        print(
            f"{item['cause']:<15}"
            f" Evidence score: "
            f"{item['score']:.1f}"
        )

    print()
    print("=" * 70)
    print(
        "DETECTIVE CONCLUSION"
    )
    print("=" * 70)

    print()
    print(
        conclusion["explanation"]
    )

    print()
    print(
        f"Strongest signal: "
        f"{conclusion['strongest_signal']}"
    )

    print(
        f"Evidence score: "
        f"{conclusion['score']:.1f}"
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

    evidence = calculate_evidence(
        data_folder
    )

    results = investigate(
        evidence
    )

    conclusion = generate_explanation(
        results
    )

    print_report(
        results,
        conclusion
    )