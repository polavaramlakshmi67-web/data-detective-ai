import pandas as pd

from src.analyzer import prepare_numeric_data


def test_prepare_numeric_data_returns_dataframe():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "quantity": [1, 2, 3],
        "category": ["A", "B", "C"],
    })

    result = prepare_numeric_data(df)

    assert isinstance(result, pd.DataFrame)


def test_prepare_numeric_data_keeps_numeric_columns():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "quantity": [1, 2, 3],
        "category": ["A", "B", "C"],
    })

    result = prepare_numeric_data(df)

    assert "revenue" in result.columns
    assert "quantity" in result.columns


def test_prepare_numeric_data_excludes_text_columns():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "category": ["A", "B", "C"],
    })

    result = prepare_numeric_data(df)

    assert "category" not in result.columns
    
    