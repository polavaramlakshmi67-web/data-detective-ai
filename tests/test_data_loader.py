import pandas as pd
import pytest

from src.data_loader import (
    load_file,
    get_dataset_info,
)


def test_load_csv(tmp_path):
    file_path = tmp_path / "sales.csv"

    df = pd.DataFrame({
        "product": ["A", "B"],
        "revenue": [100, 200],
    })

    df.to_csv(file_path, index=False)

    result = load_file(file_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "revenue" in result.columns


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_file("does_not_exist.csv")


def test_get_dataset_info():
    df = pd.DataFrame({
        "sales": [100, 200, 300],
        "category": ["A", "B", "C"],
    })

    info = get_dataset_info(df)

    assert info["rows"] == 3
    assert info["columns"] == 2
    assert "sales" in info["numeric_columns"]
    assert "category" in info["categorical_columns"]
    
    