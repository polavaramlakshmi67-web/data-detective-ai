from pathlib import Path
import pandas as pd
import numpy as np


def load_csv(file_path):
    """
    Load a CSV file into a pandas DataFrame.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(f"Dataset is empty: {file_path}")

    return df


def get_data_quality(df):
    """
    Return basic data-quality metrics.
    """
    quality = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    quality["missing_percentage"] = round(
        (quality["missing_values"] / df.size) * 100, 2
    ) if df.size else 0

    return quality


def get_numeric_summary(df):
    """
    Generate descriptive statistics for numerical columns.
    """
    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        return pd.DataFrame()

    return numeric_df.describe().T


def get_categorical_summary(df):
    """
    Generate basic summaries for categorical columns.
    """
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns

    summaries = {}

    for column in categorical_columns:
        summaries[column] = (
            df[column]
            .value_counts(dropna=False)
            .head(10)
            .to_dict()
        )

    return summaries


def find_column(df, possible_names):
    """
    Find a column using flexible name matching.
    """
    normalized = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in df.columns
    }

    for name in possible_names:
        key = name.strip().lower().replace(" ", "_")

        if key in normalized:
            return normalized[key]

    return None


def calculate_business_metrics(df):
    """
    Calculate common business metrics when matching columns exist.
    """
    metrics = {}

    sales_column = find_column(
        df,
        [
            "sales",
            "revenue",
            "amount",
            "total_sales",
            "sales_amount",
            "revenue_amount",
        ],
    )

    quantity_column = find_column(
        df,
        [
            "quantity",
            "units",
            "units_sold",
            "qty",
        ],
    )

    order_column = find_column(
        df,
        [
            "order_id",
            "orderid",
            "transaction_id",
            "transactionid",
        ],
    )

    customer_column = find_column(
        df,
        [
            "customer_id",
            "customerid",
            "customer",
        ],
    )

    if sales_column:
        sales = pd.to_numeric(df[sales_column], errors="coerce")

        metrics["sales_column"] = sales_column
        metrics["total_sales"] = round(float(sales.sum()), 2)
        metrics["average_sales"] = round(float(sales.mean()), 2)
        metrics["median_sales"] = round(float(sales.median()), 2)
        metrics["minimum_sales"] = round(float(sales.min()), 2)
        metrics["maximum_sales"] = round(float(sales.max()), 2)

    if quantity_column:
        quantity = pd.to_numeric(
            df[quantity_column],
            errors="coerce"
        )

        metrics["quantity_column"] = quantity_column
        metrics["total_quantity"] = round(float(quantity.sum()), 2)

    if order_column:
        metrics["order_column"] = order_column
        metrics["unique_orders"] = int(df[order_column].nunique())

    if customer_column:
        metrics["customer_column"] = customer_column
        metrics["unique_customers"] = int(
            df[customer_column].nunique()
        )

    return metrics


def get_grouped_metric(df, group_column, metric_column, agg="sum"):
    """
    Aggregate a numerical metric by a categorical column.
    """
    if group_column not in df.columns:
        raise ValueError(f"Column not found: {group_column}")

    if metric_column not in df.columns:
        raise ValueError(f"Column not found: {metric_column}")

    temp = df[[group_column, metric_column]].copy()

    temp[metric_column] = pd.to_numeric(
        temp[metric_column],
        errors="coerce"
    )

    result = (
        temp.groupby(group_column, dropna=False)[metric_column]
        .agg(agg)
        .reset_index()
        .sort_values(metric_column, ascending=False)
    )

    return result


def prepare_numeric_data(df):
    """
    Return clean numerical data suitable for anomaly detection.
    """
    numeric_df = df.select_dtypes(include=np.number).copy()

    numeric_df = numeric_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    numeric_df = numeric_df.dropna(axis=1, how="all")

    if numeric_df.empty:
        return pd.DataFrame()

    numeric_df = numeric_df.fillna(
        numeric_df.median(numeric_only=True)
    )

    return numeric_df