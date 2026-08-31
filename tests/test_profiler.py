import pandas as pd


def test_profiler_module_imports():
    import src.profiler

    assert src.profiler is not None


def test_profiler_has_functions():
    import src.profiler

    functions = [
        name
        for name in dir(src.profiler)
        if callable(getattr(src.profiler, name))
        and not name.startswith("_")
    ]

    assert len(functions) > 0


def test_profiler_accepts_dataframe():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "category": ["A", "B", "A"],
        "quantity": [1, 2, 3],
    })

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert len(df.columns) == 3


def test_profiler_data_contains_numeric_columns():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "category": ["A", "B", "A"],
    })

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    assert "revenue" in numeric_columns


def test_profiler_data_contains_categorical_columns():
    df = pd.DataFrame({
        "revenue": [100, 200, 300],
        "category": ["A", "B", "A"],
    })

    categorical_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    assert "category" in categorical_columns