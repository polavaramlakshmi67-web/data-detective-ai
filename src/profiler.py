from pathlib import Path

import pandas as pd


def profile_dataframe(
    df: pd.DataFrame,
    filename: str,
) -> dict:
    """Create a data-quality profile for a DataFrame."""

    if df.empty:
        return {
            "filename": filename,
            "rows": 0,
            "columns": len(df.columns),
            "duplicate_rows": 0,
            "memory_mb": 0,
            "columns_info": [],
        }

    missing = df.isna().sum()

    missing_percent = (
        missing / len(df) * 100
    ).round(2)

    profile = {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "memory_mb": round(
            df.memory_usage(deep=True).sum()
            / (1024 ** 2),
            2,
        ),
        "columns_info": [],
    }

    for column in df.columns:

        column_info = {
            "column": column,
            "dtype": str(df[column].dtype),
            "missing": int(
                missing[column]
            ),
            "missing_percent": float(
                missing_percent[column]
            ),
            "unique_values": int(
                df[column].nunique(
                    dropna=True
                )
            ),
        }

        profile["columns_info"].append(
            column_info
        )

    return profile


def profile_file(filepath):
    """Load and profile one CSV file."""

    filepath = Path(filepath)

    df = pd.read_csv(filepath)

    return profile_dataframe(
        df,
        filepath.name,
    )


def profile_all_csvs(data_folder):
    """Profile every CSV file in the data folder."""

    data_folder = Path(data_folder)

    csv_files = sorted(
        data_folder.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {data_folder}"
        )

    profiles = []

    for filepath in csv_files:

        profile = profile_file(
            filepath
        )

        profiles.append(profile)

    return profiles


def print_profile(profile):
    """Print a readable profile."""

    print()
    print("=" * 70)
    print(
        f"FILE: {profile['filename']}"
    )
    print("=" * 70)

    print(
        f"Rows:             "
        f"{profile['rows']:,}"
    )

    print(
        f"Columns:          "
        f"{profile['columns']}"
    )

    print(
        f"Duplicate rows:   "
        f"{profile['duplicate_rows']:,}"
    )

    print(
        f"Memory usage:     "
        f"{profile['memory_mb']} MB"
    )

    print()
    print("COLUMN DETAILS")
    print("-" * 70)

    for column in profile[
        "columns_info"
    ]:

        print(
            f"{column['column']:<20}"
            f" | type={column['dtype']:<12}"
            f" | missing={column['missing']:<5}"
            f" | unique={column['unique_values']:<6}"
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

    profiles = profile_all_csvs(
        data_folder
    )

    print()
    print(
        "DATA DETECTIVE — "
        "INITIAL INVESTIGATION"
    )

    for profile in profiles:

        print_profile(profile)

    print()
    print(
        "Investigation complete."
    )