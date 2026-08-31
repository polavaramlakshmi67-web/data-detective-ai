"""
Data Detective AI - Data Cleaning Module

Provides reusable functions for:
- Standardizing column names
- Removing duplicate rows
- Handling missing values
- Converting data types
- Cleaning text values
- Detecting invalid numeric values
- Generating data-quality summaries
"""

import re

import numpy as np
import pandas as pd


def clean_column_names(df):
    """
    Standardize column names.

    Example:
        "Order Date" -> "order_date"
        "Customer ID" -> "customer_id"
    """

    data = df.copy()

    cleaned_names = []

    for column in data.columns:

        column = str(column).strip().lower()

        column = re.sub(
            r"[^a-z0-9]+",
            "_",
            column
        )

        column = column.strip("_")

        cleaned_names.append(column)

    data.columns = cleaned_names

    return data


def remove_duplicate_rows(df):
    """
    Remove completely duplicated rows.

    Returns:
        cleaned dataframe
        number of duplicates removed
    """

    data = df.copy()

    duplicate_count = int(
        data.duplicated().sum()
    )

    data = data.drop_duplicates()

    return data, duplicate_count


def clean_text_columns(df):
    """
    Clean string/object columns.

    Operations:
    - Remove leading/trailing spaces
    - Normalize repeated whitespace
    - Convert empty strings to NaN
    """

    data = df.copy()

    text_columns = data.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        data[column] = data[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "null": pd.NA,
                "NULL": pd.NA,
            }
        )

    return data


def convert_date_columns(
    df,
    date_columns=None
):
    """
    Convert specified columns to datetime.

    Invalid dates become NaT.
    """

    data = df.copy()

    if not date_columns:
        return data

    for column in date_columns:

        if column not in data.columns:
            continue

        data[column] = pd.to_datetime(
            data[column],
            errors="coerce"
        )

    return data


def convert_numeric_columns(
    df,
    numeric_columns=None
):
    """
    Convert specified columns to numeric.

    Handles common currency and separator characters.
    """

    data = df.copy()

    if not numeric_columns:
        return data

    for column in numeric_columns:

        if column not in data.columns:
            continue

        if (
            data[column]
            .dtype
            .kind
            not in "biufc"
        ):

            data[column] = (
                data[column]
                .astype("string")
                .str.replace(
                    r"[₹$€£,%]",
                    "",
                    regex=True
                )
                .str.replace(
                    ",",
                    "",
                    regex=False
                )
                .str.strip()
            )

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    return data


def handle_missing_values(
    df,
    numeric_strategy="median",
    categorical_strategy="mode"
):
    """
    Handle missing values.

    Numeric columns:
        median by default

    Categorical columns:
        mode by default

    Returns:
        cleaned dataframe
        dictionary describing changes
    """

    data = df.copy()

    before = (
        data.isna()
        .sum()
        .to_dict()
    )

    numeric_columns = (
        data.select_dtypes(
            include=np.number
        ).columns
    )

    categorical_columns = (
        data.select_dtypes(
            include=[
                "object",
                "string",
                "category"
            ]
        ).columns
    )

    for column in numeric_columns:

        if data[column].isna().sum() == 0:
            continue

        if numeric_strategy == "median":

            value = data[column].median()

        elif numeric_strategy == "mean":

            value = data[column].mean()

        elif numeric_strategy == "zero":

            value = 0

        else:

            raise ValueError(
                "Invalid numeric_strategy. "
                "Use median, mean, or zero."
            )

        if pd.notna(value):

            data[column] = (
                data[column]
                .fillna(value)
            )

    for column in categorical_columns:

        if data[column].isna().sum() == 0:
            continue

        if categorical_strategy == "mode":

            modes = data[column].mode(
                dropna=True
            )

            if not modes.empty:
                value = modes.iloc[0]

            else:
                value = "Unknown"

        elif categorical_strategy == "unknown":

            value = "Unknown"

        else:

            raise ValueError(
                "Invalid categorical_strategy. "
                "Use mode or unknown."
            )

        data[column] = (
            data[column]
            .fillna(value)
        )

    after = (
        data.isna()
        .sum()
        .to_dict()
    )

    changes = {
        "missing_before": before,
        "missing_after": after,
    }

    return data, changes


def detect_invalid_numeric_values(
    df,
    numeric_columns=None
):
    """
    Identify negative values in numeric columns.

    Returns a dictionary containing
    invalid-value counts.
    """

    data = df.copy()

    if numeric_columns is None:

        numeric_columns = (
            data.select_dtypes(
                include=np.number
            ).columns.tolist()
        )

    invalid_values = {}

    for column in numeric_columns:

        if column not in data.columns:
            continue

        numeric_data = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        count = int(
            (numeric_data < 0).sum()
        )

        invalid_values[column] = count

    return invalid_values


def generate_quality_report(df):
    """
    Generate a complete data-quality report.
    """

    data = df.copy()

    report = {
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "duplicate_rows": int(
            data.duplicated().sum()
        ),
        "total_missing_values": int(
            data.isna().sum().sum()
        ),
        "missing_percentage": round(
            (
                data.isna().sum().sum()
                /
                max(data.size, 1)
            )
            * 100,
            2
        ),
    }

    return report


def clean_dataset(
    df,
    date_columns=None,
    numeric_columns=None,
    remove_duplicates=True,
    fill_missing=True
):
    """
    Complete data-cleaning pipeline.

    Returns:
        cleaned dataframe
        cleaning report
    """

    data = df.copy()

    original_rows = len(data)
    original_columns = len(data.columns)

    # 1. Standardize column names
    data = clean_column_names(data)

    # 2. Clean text values
    data = clean_text_columns(data)

    # 3. Convert dates
    data = convert_date_columns(
        data,
        date_columns
    )

    # 4. Convert numeric columns
    data = convert_numeric_columns(
        data,
        numeric_columns
    )

    # 5. Remove duplicates
    duplicates_removed = 0

    if remove_duplicates:

        data, duplicates_removed = (
            remove_duplicate_rows(data)
        )

    # 6. Handle missing values
    missing_changes = {}

    if fill_missing:

        data, missing_changes = (
            handle_missing_values(data)
        )

    # 7. Quality report
    quality = generate_quality_report(
        data
    )

    cleaning_report = {
        "original_rows": original_rows,
        "original_columns": original_columns,
        "final_rows": len(data),
        "final_columns": len(data.columns),
        "duplicates_removed": duplicates_removed,
        "missing_values": missing_changes,
        "quality": quality,
    }

    return data, cleaning_report