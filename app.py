from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Data Detective AI | RetailIQ",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_NAME = "Data Detective AI"
BUSINESS_NAME = "RetailIQ"
CURRENCY = "₹"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_FILES = {
    "Sales": "sales.csv",
    "Customers": "customers.csv",
    "Products": "products.csv",
    "Inventory": "inventory.csv",
    "Marketing": "marketing.csv",
    "Support": "support.csv",
}


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main {
            padding-top: 1rem;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
        }

        h1 {
            font-weight: 700;
        }

        h2 {
            font-weight: 650;
        }

        h3 {
            font-weight: 600;
        }

        .metric-card {
            padding: 18px;
            border: 1px solid #dddddd;
            border-radius: 10px;
            background-color: #ffffff;
        }

        .detective-box {
            padding: 20px;
            border: 1px solid #dddddd;
            border-radius: 10px;
            background-color: #fafafa;
        }

        .footer {
            text-align: center;
            color: #777777;
            padding: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_datasets():

    datasets = {}
    errors = []

    for dataset_name, filename in DATA_FILES.items():

        file_path = DATA_DIR / filename

        if not file_path.exists():
            errors.append(
                f"{filename} was not found."
            )
            continue

        try:

            df = pd.read_csv(
                file_path,
                low_memory=False,
            )

            datasets[dataset_name] = df

        except Exception as error:

            errors.append(
                f"{filename}: {error}"
            )

    return datasets, errors


datasets, loading_errors = load_datasets()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(df, keywords):

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        for keyword in keywords:

            if keyword in normalized:
                return column

    return None


def get_numeric_columns(df):

    return list(
        df.select_dtypes(
            include=[np.number]
        ).columns
    )


def get_date_columns(df):

    result = []

    for column in df.columns:

        series = df[column]

        if pd.api.types.is_datetime64_any_dtype(
            series
        ):
            result.append(column)
            continue

        if not (
            pd.api.types.is_object_dtype(
                series.dtype
            )
            or pd.api.types.is_string_dtype(
                series.dtype
            )
        ):
            continue

        sample = (
            series
            .dropna()
            .astype(str)
            .head(100)
        )

        if sample.empty:
            continue

        try:

            parsed = pd.to_datetime(
                sample,
                errors="coerce",
                format="mixed",
            )

            if parsed.notna().mean() >= 0.80:
                result.append(column)

        except Exception:
            continue

    return result


def format_currency(value):

    try:
        return f"{CURRENCY}{float(value):,.0f}"
    except Exception:
        return f"{CURRENCY}0"


def safe_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce",
    )


def create_profile(df):

    rows = []

    for column in df.columns:

        series = df[column]

        rows.append(
            {
                "Column": str(column),
                "Data Type": str(series.dtype),
                "Missing": int(
                    series.isna().sum()
                ),
                "Missing %": round(
                    series.isna().mean() * 100,
                    2,
                ),
                "Unique Values": int(
                    series.nunique(
                        dropna=True
                    )
                ),
            }
        )

    return pd.DataFrame(rows)


def detect_outliers(df):

    results = []

    for column in get_numeric_columns(df):

        values = safe_numeric(
            df[column]
        ).dropna()

        if len(values) < 5:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        count = int(
            (
                (values < lower)
                | (values > upper)
            ).sum()
        )

        percentage = (
            count
            / len(values)
            * 100
        )

        results.append(
            {
                "Column": str(column),
                "Outliers": count,
                "Outlier %": round(
                    percentage,
                    2,
                ),
            }
        )

    if not results:
        return pd.DataFrame()

    return (
        pd.DataFrame(results)
        .sort_values(
            "Outlier %",
            ascending=False,
        )
        .reset_index(drop=True)
    )


# ============================================================
# EMPTY DATASET CHECK
# ============================================================

if not datasets:

    st.title(APP_NAME)

    st.error(
        "No datasets were found."
    )

    st.write(
        "Place the following CSV files inside the data folder:"
    )

    st.code(
        """
data/
    sales.csv
    customers.csv
    products.csv
    inventory.csv
    marketing.csv
    support.csv
        """
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title(APP_NAME)

st.write(
    f"{BUSINESS_NAME} business analytics and "
    "automated data investigation platform."
)

st.caption(
    "Currency: Indian Rupees (INR)"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Data Detective Control Center"
)

selected_dataset = st.sidebar.selectbox(
    "Select dataset",
    list(datasets.keys()),
)

st.sidebar.divider()

st.sidebar.metric(
    "Datasets Loaded",
    len(datasets),
)

st.sidebar.metric(
    "Total Records",
    f"{sum(len(df) for df in datasets.values()):,}",
)


# ============================================================
# LOADING WARNINGS
# ============================================================

if loading_errors:

    with st.expander(
        "Dataset loading information"
    ):

        for error in loading_errors:
            st.warning(error)


# ============================================================
# DATASET REFERENCES
# ============================================================

sales = datasets.get("Sales")
customers = datasets.get("Customers")
products = datasets.get("Products")
inventory = datasets.get("Inventory")
marketing = datasets.get("Marketing")
support = datasets.get("Support")


# ============================================================
# GLOBAL SALES METRICS
# ============================================================

total_revenue = 0
total_profit = 0
total_units = 0
total_orders = 0


if sales is not None:

    revenue_column = find_column(
        sales,
        [
            "revenue",
            "sales",
            "amount",
            "total",
        ],
    )

    profit_column = find_column(
        sales,
        [
            "profit",
            "margin",
        ],
    )

    quantity_column = find_column(
        sales,
        [
            "quantity",
            "qty",
            "units",
        ],
    )

    order_column = find_column(
        sales,
        [
            "order_id",
            "order",
        ],
    )

    if revenue_column:

        total_revenue = (
            safe_numeric(
                sales[revenue_column]
            )
            .fillna(0)
            .sum()
        )

    if profit_column:

        total_profit = (
            safe_numeric(
                sales[profit_column]
            )
            .fillna(0)
            .sum()
        )

    if quantity_column:

        total_units = (
            safe_numeric(
                sales[quantity_column]
            )
            .fillna(0)
            .sum()
        )

    if order_column:

        total_orders = (
            sales[order_column]
            .nunique()
        )

    else:

        total_orders = len(sales)


# ============================================================
# GLOBAL KPI SECTION
# ============================================================

st.header(
    "RetailIQ Business Overview"
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "Revenue",
        format_currency(
            total_revenue
        ),
    )

with k2:

    st.metric(
        "Profit",
        format_currency(
            total_profit
        ),
    )

with k3:

    st.metric(
        "Orders",
        f"{total_orders:,}",
    )

with k4:

    st.metric(
        "Customers",
        (
            f"{len(customers):,}"
            if customers is not None
            else "0"
        ),
    )

with k5:

    st.metric(
        "Support Tickets",
        (
            f"{len(support):,}"
            if support is not None
            else "0"
        ),
    )


# ============================================================
# TABS
# ============================================================

(
    dashboard_tab,
    detective_tab,
    sales_tab,
    inventory_tab,
    marketing_tab,
    support_tab,
    profile_tab,
) = st.tabs(
    [
        "Dashboard",
        "AI Detective",
        "Sales Analysis",
        "Inventory",
        "Marketing",
        "Support",
        "Data Profile",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with dashboard_tab:

    st.header(
        "Business Performance Dashboard"
    )

    if sales is None:

        st.warning(
            "sales.csv is not available."
        )

    else:

        revenue_column = find_column(
            sales,
            [
                "revenue",
                "sales",
                "amount",
                "total",
            ],
        )

        region_column = find_column(
            sales,
            [
                "region",
            ],
        )

        if (
            revenue_column
            and region_column
        ):

            region_data = sales[
                [
                    region_column,
                    revenue_column,
                ]
            ].copy()

            region_data[
                revenue_column
            ] = safe_numeric(
                region_data[
                    revenue_column
                ]
            ).fillna(0)

            region_summary = (
                region_data
                .groupby(
                    region_column,
                    as_index=False,
                )[revenue_column]
                .sum()
            )

            region_summary[
                region_column
            ] = (
                region_summary[
                    region_column
                ]
                .astype(str)
            )

            st.subheader(
                "Revenue by Region"
            )

            st.bar_chart(
                region_summary,
                x=region_column,
                y=revenue_column,
                width="stretch",
            )

        date_candidates = (
            get_date_columns(sales)
        )

        if (
            revenue_column
            and date_candidates
        ):

            date_column = (
                date_candidates[0]
            )

            trend_data = sales[
                [
                    date_column,
                    revenue_column,
                ]
            ].copy()

            trend_data[
                date_column
            ] = pd.to_datetime(
                trend_data[
                    date_column
                ],
                errors="coerce",
                format="mixed",
            )

            trend_data[
                revenue_column
            ] = safe_numeric(
                trend_data[
                    revenue_column
                ]
            )

            trend_data = (
                trend_data
                .dropna()
            )

            if not trend_data.empty:

                trend_data[
                    "Month"
                ] = (
                    trend_data[
                        date_column
                    ]
                    .dt.to_period("M")
                    .astype(str)
                )

                monthly_revenue = (
                    trend_data
                    .groupby(
                        "Month",
                        as_index=False,
                    )[revenue_column]
                    .sum()
                )

                st.subheader(
                    "Monthly Revenue Trend"
                )

                st.line_chart(
                    monthly_revenue,
                    x="Month",
                    y=revenue_column,
                    width="stretch",
                )


# ============================================================
# AI DETECTIVE
# ============================================================

with detective_tab:

    st.header(
        "AI Business Detective"
    )

    st.write(
        "The detective engine evaluates available "
        "business metrics and identifies the strongest "
        "evidence-based signal."
    )

    signals = []

    # --------------------------------------------------------
    # INVENTORY SIGNAL
    # --------------------------------------------------------

    if inventory is not None:

        stock_column = find_column(
            inventory,
            [
                "stock",
                "inventory",
                "available",
            ],
        )

        if stock_column:

            stock_values = (
                safe_numeric(
                    inventory[
                        stock_column
                    ]
                )
                .dropna()
            )

            if not stock_values.empty:

                threshold = (
                    stock_values
                    .quantile(0.20)
                )

                low_stock_count = int(
                    (
                        stock_values
                        <= threshold
                    ).sum()
                )

                low_stock_percentage = (
                    low_stock_count
                    / len(stock_values)
                    * 100
                )

                inventory_score = min(
                    low_stock_percentage
                    * 1.5,
                    100,
                )

                signals.append(
                    {
                        "Signal": "Inventory",
                        "Score": inventory_score,
                        "Evidence": (
                            f"{low_stock_count:,} "
                            f"inventory records "
                            f"({low_stock_percentage:.1f}%) "
                            "are within the lowest "
                            "20% of stock levels."
                        ),
                    }
                )

    # --------------------------------------------------------
    # PROFIT SIGNAL
    # --------------------------------------------------------

    if sales is not None:

        profit_column = find_column(
            sales,
            [
                "profit",
                "margin",
            ],
        )

        if profit_column:

            profit_values = (
                safe_numeric(
                    sales[
                        profit_column
                    ]
                )
                .dropna()
            )

            if not profit_values.empty:

                negative_percentage = (
                    (
                        profit_values < 0
                    ).mean()
                    * 100
                )

                profit_score = min(
                    negative_percentage
                    * 2,
                    100,
                )

                signals.append(
                    {
                        "Signal": "Profit",
                        "Score": profit_score,
                        "Evidence": (
                            f"{negative_percentage:.1f}% "
                            "of sales records "
                            "have negative profit."
                        ),
                    }
                )

    # --------------------------------------------------------
    # CUSTOMER SUPPORT SIGNAL
    # --------------------------------------------------------

    if support is not None:

        issue_column = find_column(
            support,
            [
                "issue_type",
                "issue",
                "problem",
            ],
        )

        if issue_column:

            issue_counts = (
                support[
                    issue_column
                ]
                .astype(str)
                .value_counts()
            )

            if not issue_counts.empty:

                top_issue = str(
                    issue_counts.index[0]
                )

                top_issue_count = int(
                    issue_counts.iloc[0]
                )

                top_issue_percentage = (
                    top_issue_count
                    / len(support)
                    * 100
                )

                support_score = min(
                    top_issue_percentage
                    * 2,
                    100,
                )

                signals.append(
                    {
                        "Signal": "Customer Support",
                        "Score": support_score,
                        "Evidence": (
                            f"'{top_issue}' is the "
                            f"most common support "
                            f"issue with "
                            f"{top_issue_count:,} "
                            f"tickets "
                            f"({top_issue_percentage:.1f}%)."
                        ),
                    }
                )

    # --------------------------------------------------------
    # MARKETING SIGNAL
    # --------------------------------------------------------

    if marketing is not None:

        spend_column = find_column(
            marketing,
            [
                "spend",
                "marketing",
                "cost",
            ],
        )

        clicks_column = find_column(
            marketing,
            [
                "click",
                "clicks",
            ],
        )

        if (
            spend_column
            and clicks_column
        ):

            spend_values = (
                safe_numeric(
                    marketing[
                        spend_column
                    ]
                )
                .fillna(0)
            )

            click_values = (
                safe_numeric(
                    marketing[
                        clicks_column
                    ]
                )
                .fillna(0)
            )

            total_spend = (
                spend_values.sum()
            )

            total_clicks = (
                click_values.sum()
            )

            if total_spend > 0:

                cost_per_click = (
                    total_spend
                    / max(
                        total_clicks,
                        1,
                    )
                )

                marketing_score = min(
                    cost_per_click
                    / 10,
                    100,
                )

                signals.append(
                    {
                        "Signal": "Marketing",
                        "Score": marketing_score,
                        "Evidence": (
                            f"Marketing spend is "
                            f"{format_currency(total_spend)} "
                            f"for "
                            f"{total_clicks:,.0f} "
                            "clicks. Average "
                            f"cost per click is "
                            f"{format_currency(cost_per_click)}."
                        ),
                    }
                )

    # --------------------------------------------------------
    # SALES ANOMALY SIGNAL
    # --------------------------------------------------------

    if sales is not None:

        sales_outliers = (
            detect_outliers(sales)
        )

        if not sales_outliers.empty:

            strongest_outlier = (
                sales_outliers.iloc[0]
            )

            anomaly_score = min(
                float(
                    strongest_outlier[
                        "Outlier %"
                    ]
                )
                * 2,
                100,
            )

            signals.append(
                {
                    "Signal": "Sales Anomaly",
                    "Score": anomaly_score,
                    "Evidence": (
                        f"{strongest_outlier['Column']} "
                        f"contains "
                        f"{strongest_outlier['Outlier %']:.1f}% "
                        "potential outliers."
                    ),
                }
            )

    # --------------------------------------------------------
    # SELECT STRONGEST SIGNAL
    # --------------------------------------------------------

    if signals:

        strongest_signal = max(
            signals,
            key=lambda item: item["Score"],
        )

    else:

        strongest_signal = {
            "Signal": "Data Quality",
            "Score": 0.0,
            "Evidence": (
                "The dataset does not contain enough "
                "business metrics for deeper analysis."
            ),
        }

    # --------------------------------------------------------
    # DETECTIVE KPIs
    # --------------------------------------------------------

    st.divider()

    d1, d2 = st.columns(2)

    with d1:

        st.metric(
            "Strongest Signal",
            strongest_signal[
                "Signal"
            ],
        )

    with d2:

        st.metric(
            "Evidence Score",
            f"{strongest_signal['Score']:.1f}/100",
        )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.subheader(
        "Evidence"
    )

    st.info(
        strongest_signal[
            "Evidence"
        ]
    )

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    st.subheader(
        "Recommended Action"
    )

    signal_name = (
        strongest_signal["Signal"]
    )

    if signal_name == "Inventory":

        recommendation = (
            "Review low-stock products against sales "
            "demand. Prioritize replenishment for products "
            "showing strong demand and low available stock."
        )

    elif signal_name == "Profit":

        recommendation = (
            "Investigate negative-profit transactions. "
            "Review product costs, pricing, discounts and "
            "regional performance to identify margin pressure."
        )

    elif signal_name == "Customer Support":

        recommendation = (
            "Investigate the most frequent customer issue. "
            "Segment the issue by product, region and date "
            "to identify the underlying cause."
        )

    elif signal_name == "Marketing":

        recommendation = (
            "Compare campaign spending with clicks and "
            "downstream sales. Prioritize campaigns that "
            "generate measurable business value."
        )

    elif signal_name == "Sales Anomaly":

        recommendation = (
            "Investigate unusual sales records and compare "
            "them by product, customer, region and date. "
            "Determine whether anomalies represent real "
            "business events or data-quality problems."
        )

    else:

        recommendation = (
            "Add additional business metrics such as "
            "revenue, profit, cost, inventory or customer "
            "information for deeper analysis."
        )

    st.warning(
        recommendation
    )

    # --------------------------------------------------------
    # EVIDENCE BOARD
    # --------------------------------------------------------

    st.subheader(
        "Evidence Board"
    )

    if signals:

        evidence_table = pd.DataFrame(
            [
                {
                    "Signal": item[
                        "Signal"
                    ],
                    "Evidence Score": round(
                        item["Score"],
                        1,
                    ),
                    "Evidence": item[
                        "Evidence"
                    ],
                }
                for item in sorted(
                    signals,
                    key=lambda item:
                    item["Score"],
                    reverse=True,
                )
            ]
        )

        st.dataframe(
            evidence_table,
            width="stretch",
            hide_index=True,
        )

        evidence_chart = (
            evidence_table[
                [
                    "Signal",
                    "Evidence Score",
                ]
            ]
            .copy()
        )

        evidence_chart[
            "Signal"
        ] = (
            evidence_chart[
                "Signal"
            ].astype(str)
        )

        evidence_chart[
            "Evidence Score"
        ] = safe_numeric(
            evidence_chart[
                "Evidence Score"
            ]
        ).fillna(0)

        st.bar_chart(
            evidence_chart,
            x="Signal",
            y="Evidence Score",
            width="stretch",
        )

    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    st.subheader(
        "Detective Conclusion"
    )

    st.write(
        f"Strongest signal: "
        f"{strongest_signal['Signal']}"
    )

    st.write(
        f"Evidence score: "
        f"{strongest_signal['Score']:.1f}/100"
    )

    st.write(
        f"Finding: "
        f"{strongest_signal['Evidence']}"
    )

    st.success(
        "Data investigation completed successfully."
    )


# ============================================================
# SALES ANALYSIS
# ============================================================

with sales_tab:

    st.header(
        "Sales Analysis"
    )

    if sales is None:

        st.warning(
            "sales.csv is not available."
        )

    else:

        revenue_column = find_column(
            sales,
            [
                "revenue",
                "sales",
                "amount",
                "total",
            ],
        )

        profit_column = find_column(
            sales,
            [
                "profit",
                "margin",
            ],
        )

        product_column = find_column(
            sales,
            [
                "product_id",
                "product",
                "sku",
            ],
        )

        if revenue_column:

            sales_analysis = sales.copy()

            sales_analysis[
                revenue_column
            ] = safe_numeric(
                sales_analysis[
                    revenue_column
                ]
            ).fillna(0)

            if product_column:

                product_revenue = (
                    sales_analysis[
                        [
                            product_column,
                            revenue_column,
                        ]
                    ]
                    .groupby(
                        product_column,
                        as_index=False,
                    )[revenue_column]
                    .sum()
                    .sort_values(
                        revenue_column,
                        ascending=False,
                    )
                    .head(15)
                )

                product_revenue[
                    product_column
                ] = (
                    product_revenue[
                        product_column
                    ]
                    .astype(str)
                )

                st.subheader(
                    "Top Products by Revenue"
                )

                st.bar_chart(
                    product_revenue,
                    x=product_column,
                    y=revenue_column,
                    width="stretch",
                )

        if profit_column:

            profit_values = safe_numeric(
                sales[
                    profit_column
                ]
            )

            profit_values = (
                profit_values
                .dropna()
            )

            if not profit_values.empty:

                st.subheader(
                    "Profit Distribution"
                )

                profit_chart = pd.DataFrame(
                    {
                        "Record": np.arange(
                            len(
                                profit_values
                            )
                        ),
                        "Profit": (
                            profit_values
                            .to_numpy()
                        ),
                    }
                )

                st.line_chart(
                    profit_chart,
                    x="Record",
                    y="Profit",
                    width="stretch",
                )


# ============================================================
# INVENTORY ANALYSIS
# ============================================================

with inventory_tab:

    st.header(
        "Inventory Investigation"
    )

    if inventory is None:

        st.warning(
            "inventory.csv is not available."
        )

    else:

        stock_column = find_column(
            inventory,
            [
                "stock",
                "inventory",
                "available",
            ],
        )

        product_column = find_column(
            inventory,
            [
                "product_id",
                "product",
                "sku",
            ],
        )

        if stock_column:

            inventory_data = (
                inventory.copy()
            )

            inventory_data[
                stock_column
            ] = safe_numeric(
                inventory_data[
                    stock_column
                ]
            )

            stock_values = (
                inventory_data[
                    stock_column
                ]
                .dropna()
            )

            if not stock_values.empty:

                low_threshold = (
                    stock_values
                    .quantile(0.20)
                )

                low_stock = (
                    inventory_data[
                        inventory_data[
                            stock_column
                        ]
                        <= low_threshold
                    ]
                )

                i1, i2, i3 = (
                    st.columns(3)
                )

                with i1:

                    st.metric(
                        "Inventory Records",
                        f"{len(inventory):,}",
                    )

                with i2:

                    st.metric(
                        "Low Stock Records",
                        f"{len(low_stock):,}",
                    )

                with i3:

                    st.metric(
                        "Low Stock Threshold",
                        f"{low_threshold:,.0f}",
                    )

                if product_column:

                    product_stock = (
                        inventory_data[
                            [
                                product_column,
                                stock_column,
                            ]
                        ]
                        .dropna()
                        .groupby(
                            product_column,
                            as_index=False,
                        )[stock_column]
                        .mean()
                        .sort_values(
                            stock_column
                        )
                        .head(15)
                    )

                    product_stock[
                        product_column
                    ] = (
                        product_stock[
                            product_column
                        ]
                        .astype(str)
                    )

                    st.subheader(
                        "Products with Lowest Average Stock"
                    )

                    st.bar_chart(
                        product_stock,
                        x=product_column,
                        y=stock_column,
                        width="stretch",
                    )


# ============================================================
# MARKETING ANALYSIS
# ============================================================

with marketing_tab:

    st.header(
        "Marketing Investigation"
    )

    if marketing is None:

        st.warning(
            "marketing.csv is not available."
        )

    else:

        spend_column = find_column(
            marketing,
            [
                "spend",
                "marketing",
                "cost",
            ],
        )

        clicks_column = find_column(
            marketing,
            [
                "click",
                "clicks",
            ],
        )

        if spend_column:

            marketing_data = (
                marketing.copy()
            )

            marketing_data[
                spend_column
            ] = safe_numeric(
                marketing_data[
                    spend_column
                ]
            ).fillna(0)

            total_spend = (
                marketing_data[
                    spend_column
                ].sum()
            )

            m1, m2 = (
                st.columns(2)
            )

            with m1:

                st.metric(
                    "Marketing Spend",
                    format_currency(
                        total_spend
                    ),
                )

            if clicks_column:

                marketing_data[
                    clicks_column
                ] = safe_numeric(
                    marketing_data[
                        clicks_column
                    ]
                ).fillna(0)

                total_clicks = (
                    marketing_data[
                        clicks_column
                    ].sum()
                )

                with m2:

                    st.metric(
                        "Campaign Clicks",
                        f"{total_clicks:,.0f}",
                    )

                campaign_chart = pd.DataFrame(
                    {
                        "Campaign": np.arange(
                            1,
                            len(
                                marketing_data
                            )
                            + 1,
                        ),
                        "Clicks": (
                            marketing_data[
                                clicks_column
                            ]
                            .to_numpy()
                        ),
                    }
                )

                st.subheader(
                    "Campaign Click Activity"
                )

                st.line_chart(
                    campaign_chart,
                    x="Campaign",
                    y="Clicks",
                    width="stretch",
                )


# ============================================================
# CUSTOMER SUPPORT ANALYSIS
# ============================================================

with support_tab:

    st.header(
        "Customer Support Investigation"
    )

    if support is None:

        st.warning(
            "support.csv is not available."
        )

    else:

        issue_column = find_column(
            support,
            [
                "issue_type",
                "issue",
                "problem",
            ],
        )

        region_column = find_column(
            support,
            [
                "region",
            ],
        )

        s1, s2, s3 = (
            st.columns(3)
        )

        with s1:

            st.metric(
                "Support Tickets",
                f"{len(support):,}",
            )

        with s2:

            st.metric(
                "Issue Types",
                (
                    support[
                        issue_column
                    ].nunique()
                    if issue_column
                    else 0
                ),
            )

        with s3:

            st.metric(
                "Regions",
                (
                    support[
                        region_column
                    ].nunique()
                    if region_column
                    else 0
                ),
            )

        if issue_column:

            issue_summary = (
                support[
                    issue_column
                ]
                .astype(str)
                .value_counts()
                .reset_index()
            )

            issue_summary.columns = [
                "Issue",
                "Tickets",
            ]

            st.subheader(
                "Most Common Customer Issues"
            )

            st.bar_chart(
                issue_summary,
                x="Issue",
                y="Tickets",
                width="stretch",
            )

            st.dataframe(
                issue_summary,
                width="stretch",
                hide_index=True,
            )


# ============================================================
# DATA PROFILE
# ============================================================

with profile_tab:

    selected_df = datasets[
        selected_dataset
    ]

    st.header(
        f"{selected_dataset} Data Profile"
    )

    p1, p2, p3, p4 = (
        st.columns(4)
    )

    with p1:

        st.metric(
            "Rows",
            f"{len(selected_df):,}",
        )

    with p2:

        st.metric(
            "Columns",
            f"{len(selected_df.columns):,}",
        )

    with p3:

        st.metric(
            "Missing Values",
            f"{selected_df.isna().sum().sum():,}",
        )

    with p4:

        st.metric(
            "Duplicate Rows",
            f"{selected_df.duplicated().sum():,}",
        )

    st.subheader(
        "Column Details"
    )

    st.dataframe(
        create_profile(
            selected_df
        ),
        width="stretch",
        hide_index=True,
    )

    numeric = (
        get_numeric_columns(
            selected_df
        )
    )

    if numeric:

        st.subheader(
            "Numeric Summary"
        )

        numeric_data = (
            selected_df[
                numeric
            ]
            .apply(
                pd.to_numeric,
                errors="coerce",
            )
        )

        numeric_summary = (
            numeric_data
            .describe()
            .T
            .round(2)
            .reset_index()
        )

        numeric_summary = (
            numeric_summary
            .rename(
                columns={
                    "index": "Column"
                }
            )
        )

        st.dataframe(
            numeric_summary,
            width="stretch",
            hide_index=True,
        )

    outliers = detect_outliers(
        selected_df
    )

    if not outliers.empty:

        st.subheader(
            "Potential Numerical Outliers"
        )

        st.dataframe(
            outliers,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    f"Preview {selected_dataset} data"
):

    st.dataframe(
        datasets[
            selected_dataset
        ].head(100),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        Data Detective AI | RetailIQ Business Analytics<br>
        Automated profiling | Anomaly detection |
        Trend analysis | Business recommendations |
        Currency: INR
    </div>
    """,
    unsafe_allow_html=True,
)


