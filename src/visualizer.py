"""
Data Detective AI - Visualization Module

Reusable visualization functions for business analytics,
data quality, trends, KPIs, and anomaly detection.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_or_show(fig, output_path=None):
    """
    Save a matplotlib figure if output_path is provided.
    Otherwise display it.
    """
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fig.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close(fig)

    else:
        plt.show()


def plot_missing_values(
    df,
    output_path=None,
    top_n=15
):
    """
    Plot columns with the highest number of missing values.
    """

    missing = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing = missing[missing > 0].head(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))

    if missing.empty:
        ax.text(
            0.5,
            0.5,
            "No missing values detected",
            ha="center",
            va="center",
            fontsize=14
        )

        ax.set_axis_off()

    else:
        missing.sort_values().plot(
            kind="barh",
            ax=ax
        )

        ax.set_title(
            "Missing Values by Column"
        )

        ax.set_xlabel(
            "Number of Missing Values"
        )

        ax.set_ylabel(
            "Column"
        )

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def plot_numeric_distribution(
    df,
    column,
    output_path=None,
    bins=30
):
    """
    Plot the distribution of a numeric column.
    """

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found."
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):
        raise ValueError(
            f"Column '{column}' is not numeric."
        )

    values = df[column].dropna()

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    ax.hist(
        values,
        bins=bins
    )

    ax.set_title(
        f"Distribution of {column}"
    )

    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def plot_time_series(
    df,
    date_column,
    value_column,
    output_path=None,
    frequency="D"
):
    """
    Plot a time-series trend.
    """

    if date_column not in df.columns:
        raise ValueError(
            f"Column '{date_column}' not found."
        )

    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' not found."
        )

    data = df[
        [date_column, value_column]
    ].copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna()

    if data.empty:
        raise ValueError(
            "No valid data available for the time series."
        )

    trend = (
        data
        .set_index(date_column)[value_column]
        .resample(frequency)
        .sum()
    )

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    ax.plot(
        trend.index,
        trend.values
    )

    ax.set_title(
        f"{value_column} Trend"
    )

    ax.set_xlabel(
        "Date"
    )

    ax.set_ylabel(
        value_column
    )

    ax.tick_params(
        axis="x",
        rotation=30
    )

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def plot_category_performance(
    df,
    category_column,
    value_column,
    output_path=None,
    top_n=10
):
    """
    Plot performance by category.
    """

    required = [
        category_column,
        value_column
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    data = df[
        required
    ].copy()

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna()

    performance = (
        data
        .groupby(category_column)[value_column]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    performance.sort_values().plot(
        kind="barh",
        ax=ax
    )

    ax.set_title(
        f"Top {top_n} {category_column} by "
        f"{value_column}"
    )

    ax.set_xlabel(
        value_column
    )

    ax.set_ylabel(
        category_column
    )

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def plot_anomalies(
    df,
    value_column,
    anomaly_column="is_anomaly",
    output_path=None
):
    """
    Visualize normal observations versus anomalies.
    """

    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' not found."
        )

    if anomaly_column not in df.columns:
        raise ValueError(
            f"Column '{anomaly_column}' not found."
        )

    data = df.copy()

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[value_column]
    )

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    normal = data[
        data[anomaly_column] == False
    ]

    anomalies = data[
        data[anomaly_column] == True
    ]

    ax.scatter(
        normal.index,
        normal[value_column],
        label="Normal"
    )

    ax.scatter(
        anomalies.index,
        anomalies[value_column],
        label="Anomaly"
    )

    ax.set_title(
        f"Anomaly Detection: {value_column}"
    )

    ax.set_xlabel(
        "Record"
    )

    ax.set_ylabel(
        value_column
    )

    ax.legend()

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def plot_kpi_summary(
    metrics,
    output_path=None
):
    """
    Create a simple KPI summary chart.

    metrics should be a dictionary containing
    numeric KPI values.
    """

    numeric_metrics = {}

    for key, value in metrics.items():

        try:
            numeric_value = float(value)

            if pd.notna(numeric_value):
                numeric_metrics[key] = numeric_value

        except (
            TypeError,
            ValueError
        ):
            continue

    if not numeric_metrics:
        raise ValueError(
            "No numeric KPIs available."
        )

    labels = list(
        numeric_metrics.keys()
    )

    values = list(
        numeric_metrics.values()
    )

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    ax.bar(
        labels,
        values
    )

    ax.set_title(
        "Business KPI Summary"
    )

    ax.set_ylabel(
        "Value"
    )

    ax.tick_params(
        axis="x",
        rotation=30
    )

    fig.tight_layout()

    _save_or_show(
        fig,
        output_path
    )


def create_business_visualizations(
    df,
    output_dir,
    date_column=None,
    value_column=None,
    category_column=None,
    anomaly_column=None
):
    """
    Create a collection of useful business charts.

    Returns a dictionary containing generated
    chart paths.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    charts = {}

    if date_column and value_column:

        path = (
            output_dir /
            "business_trend.png"
        )

        plot_time_series(
            df,
            date_column,
            value_column,
            path,
            frequency="D"
        )

        charts["trend"] = path

    if category_column and value_column:

        path = (
            output_dir /
            "category_performance.png"
        )

        plot_category_performance(
            df,
            category_column,
            value_column,
            path
        )

        charts["category_performance"] = path

    if anomaly_column and value_column:

        path = (
            output_dir /
            "anomalies.png"
        )

        plot_anomalies(
            df,
            value_column,
            anomaly_column,
            path
        )

        charts["anomalies"] = path

    path = (
        output_dir /
        "missing_values.png"
    )

    plot_missing_values(
        df,
        path
    )

    charts["missing_values"] = path

    return charts