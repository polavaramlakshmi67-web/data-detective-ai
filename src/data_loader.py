"""
Data Detective AI - Data Loading Module

Handles:
- CSV loading
- Excel loading
- Multiple dataset loading
- File validation
- Basic loading statistics
"""

from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}


def validate_file(file_path):
    """
    Validate that a data file exists and has a supported format.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. "
            f"Supported formats: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    return path


def load_file(file_path):
    """
    Load a single CSV or Excel file.

    Returns:
        pandas.DataFrame
    """

    path = validate_file(file_path)

    extension = path.suffix.lower()

    try:

        if extension == ".csv":

            df = pd.read_csv(
                path
            )

        elif extension in {".xlsx", ".xls"}:

            df = pd.read_excel(
                path
            )

        else:

            raise ValueError(
                f"Unsupported file format: {extension}"
            )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"The file is empty: {path.name}"
        )

    except pd.errors.ParserError as error:

        raise ValueError(
            f"Could not parse {path.name}: {error}"
        )

    except Exception as error:

        raise RuntimeError(
            f"Failed to load {path.name}: {error}"
        )

    if df.empty:

        raise ValueError(
            f"The dataset contains no rows: {path.name}"
        )

    return df


def load_csv(file_path):
    """
    Load a CSV file.
    """

    path = Path(file_path)

    if path.suffix.lower() != ".csv":

        raise ValueError(
            "load_csv() expects a CSV file."
        )

    return load_file(path)


def load_excel(file_path):
    """
    Load an Excel file.
    """

    path = Path(file_path)

    if path.suffix.lower() not in {
        ".xlsx",
        ".xls"
    }:

        raise ValueError(
            "load_excel() expects an Excel file."
        )

    return load_file(path)


def load_directory(
    data_folder,
    recursive=False
):
    """
    Load all supported datasets from a directory.

    Returns:
        Dictionary:
            {
                "sales": DataFrame,
                "inventory": DataFrame,
                ...
            }
    """

    folder = Path(data_folder)

    if not folder.exists():

        raise FileNotFoundError(
            f"Data directory not found: {folder}"
        )

    if not folder.is_dir():

        raise ValueError(
            f"Expected a directory: {folder}"
        )

    if recursive:

        files = [
            path
            for path in folder.rglob("*")
            if path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ]

    else:

        files = [
            path
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ]

    if not files:

        raise FileNotFoundError(
            f"No supported data files found in {folder}"
        )

    datasets = {}

    for path in sorted(files):

        try:

            datasets[path.stem] = load_file(
                path
            )

        except Exception as error:

            print(
                f"Warning: Could not load "
                f"{path.name}: {error}"
            )

    if not datasets:

        raise RuntimeError(
            "None of the datasets could be loaded."
        )

    return datasets


def load_business_datasets(
    data_folder
):
    """
    Load the four core Data Detective AI
    business datasets.

    Expected files:

        sales.csv
        inventory.csv
        support.csv
        marketing.csv

    Returns:
        Dictionary of DataFrames.
    """

    folder = Path(data_folder)

    required_files = [
        "sales.csv",
        "inventory.csv",
        "support.csv",
        "marketing.csv",
    ]

    datasets = {}

    missing_files = []

    for filename in required_files:

        path = folder / filename

        if not path.exists():

            missing_files.append(
                filename
            )

            continue

        datasets[
            Path(filename).stem
        ] = load_file(path)

    if missing_files:

        raise FileNotFoundError(
            "Missing required business datasets: "
            + ", ".join(missing_files)
        )

    return datasets


def get_dataset_info(df):
    """
    Return useful information about a dataset.
    """

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "missing_values": int(
            df.isna().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "numeric_columns": (
            df.select_dtypes(
                include="number"
            )
            .columns
            .tolist()
        ),
        "categorical_columns": (
            df.select_dtypes(
                include=[
                    "object",
                    "string",
                    "category",
                ]
            )
            .columns
            .tolist()
        ),
    }


def print_dataset_summary(
    datasets
):
    """
    Print a readable summary of loaded datasets.
    """

    print()
    print("=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    for name, df in datasets.items():

        info = get_dataset_info(df)

        print()
        print(f"Dataset: {name}")
        print("-" * 70)
        print(
            f"Rows:              {info['rows']:,}"
        )
        print(
            f"Columns:           {info['columns']:,}"
        )
        print(
            f"Missing values:    {info['missing_values']:,}"
        )
        print(
            f"Duplicate rows:    {info['duplicate_rows']:,}"
        )

        print(
            f"Numeric columns:   "
            f"{len(info['numeric_columns'])}"
        )

        print(
            f"Categorical cols:  "
            f"{len(info['categorical_columns'])}"
        )

    print()
    print("=" * 70)


def save_dataset(
    df,
    output_path
):
    """
    Save a DataFrame as CSV.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    return output_path