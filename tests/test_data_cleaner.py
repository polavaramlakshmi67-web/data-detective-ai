import pandas as pd

from src.data_cleaner import (
    clean_column_names,
    remove_duplicate_rows,
    clean_text_columns,
    generate_quality_report,
)


def test_clean_column_names():
    df = pd.DataFrame({
        "Customer Name": ["Alice", "Bob"],
        "Order Date": ["2026-01-01", "2026-01-02"],
    })

    result = clean_column_names(df)

    assert "customer_name" in result.columns
    assert "order_date" in result.columns


def test_remove_duplicate_rows():
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "value": [100, 100, 200],
    })

    result, removed = remove_duplicate_rows(df)

    assert len(result) == 2
    assert removed == 1


def test_clean_text_columns():
    df = pd.DataFrame({
        "name": ["  Alice  ", " Bob "],
    })

    result = clean_text_columns(df)

    assert result["name"].iloc[0] == "Alice"
    assert result["name"].iloc[1] == "Bob"


def test_generate_quality_report():
    df = pd.DataFrame({
        "sales": [100, 200, None],
        "category": ["A", "B", "B"],
    })

    report = generate_quality_report(df)

    assert report["rows"] == 3
    assert report["columns"] == 2
    assert report["total_missing_values"] == 1