from pathlib import Path

from src.analyzer import (
    load_csv,
    get_data_quality,
    get_numeric_summary,
    calculate_business_metrics,
)

from src.anomaly_detector import (
    detect_anomalies,
    get_anomaly_summary,
)

from src.ai_insights import (
    generate_insights,
    insights_to_dataframe,
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "reports"


def ensure_directories():
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)


def analyze_dataset(file_path, dataset_name):

    print("\n" + "=" * 60)
    print(f"ANALYZING: {dataset_name}")
    print("=" * 60)

    df = load_csv(file_path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    # Data quality
    quality = get_data_quality(df)

    print("\nDATA QUALITY")
    print("-" * 40)

    for key, value in quality.items():
        print(f"{key}: {value}")

    # Business metrics
    metrics = calculate_business_metrics(df)

    print("\nBUSINESS METRICS")
    print("-" * 40)

    for key, value in metrics.items():
        print(f"{key}: {value}")

    # Numeric summary
    numeric_summary = get_numeric_summary(df)

    if not numeric_summary.empty:
        numeric_summary.to_csv(
            OUTPUT_DIR / f"{dataset_name}_numeric_summary.csv"
        )

    # Anomaly detection
    anomaly_df = detect_anomalies(df)

    anomaly_summary = get_anomaly_summary(
        anomaly_df
    )

    print("\nANOMALY DETECTION")
    print("-" * 40)

    for key, value in anomaly_summary.items():
        print(f"{key}: {value}")

    # Save anomalies
    anomaly_output = anomaly_df[
        anomaly_df["is_anomaly"] == True
    ].copy()

    anomaly_output.to_csv(
        OUTPUT_DIR / f"{dataset_name}_anomalies.csv",
        index=False,
    )

    # Generate insights
    insights = generate_insights(
        df,
        anomaly_df
    )

    insights_df = insights_to_dataframe(
        insights
    )

    insights_df.to_csv(
        OUTPUT_DIR / f"{dataset_name}_insights.csv",
        index=False,
    )

    return {
        "df": df,
        "quality": quality,
        "metrics": metrics,
        "anomaly_df": anomaly_df,
        "anomaly_summary": anomaly_summary,
        "insights": insights,
    }


def build_summary(results):

    rows = []

    for dataset_name, result in results.items():

        metrics = result["metrics"]
        quality = result["quality"]
        anomalies = result["anomaly_summary"]

        rows.append(
            {
                "dataset": dataset_name,
                "rows": quality["rows"],
                "columns": quality["columns"],
                "missing_values": quality[
                    "missing_values"
                ],
                "duplicate_rows": quality[
                    "duplicate_rows"
                ],
                "total_sales": metrics.get(
                    "total_sales"
                ),
                "average_sales": metrics.get(
                    "average_sales"
                ),
                "anomalies": anomalies[
                    "anomalies"
                ],
                "anomaly_percentage": anomalies[
                    "anomaly_percentage"
                ],
            }
        )

    summary_df = __import__(
        "pandas"
    ).DataFrame(rows)

    summary_df.to_csv(
        OUTPUT_DIR / "summary.csv",
        index=False
    )

    return summary_df


def build_report(results):

    report_path = (
        REPORT_DIR /
        "novamart_investigation.md"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "# NovaMart Data Investigation\n\n"
        )

        report.write(
            "## Executive Summary\n\n"
        )

        report.write(
            "Data Detective AI analyzed the available "
            "business datasets to identify data-quality "
            "issues, business metrics, unusual observations, "
            "and potential areas for further investigation.\n\n"
        )

        for dataset_name, result in results.items():

            report.write(
                f"## Dataset: {dataset_name}\n\n"
            )

            quality = result["quality"]
            metrics = result["metrics"]
            anomalies = result["anomaly_summary"]

            report.write(
                "### Data Quality\n\n"
            )

            report.write(
                f"- Rows: {quality['rows']:,}\n"
            )

            report.write(
                f"- Columns: {quality['columns']:,}\n"
            )

            report.write(
                f"- Missing values: "
                f"{quality['missing_values']:,}\n"
            )

            report.write(
                f"- Duplicate rows: "
                f"{quality['duplicate_rows']:,}\n\n"
            )

            report.write(
                "### Business Metrics\n\n"
            )

            for key, value in metrics.items():

                report.write(
                    f"- {key}: {value}\n"
                )

            report.write("\n")

            report.write(
                "### Anomaly Detection\n\n"
            )

            report.write(
                f"- Total records: "
                f"{anomalies['total_records']:,}\n"
            )

            report.write(
                f"- Anomalies: "
                f"{anomalies['anomalies']:,}\n"
            )

            report.write(
                f"- Anomaly rate: "
                f"{anomalies['anomaly_percentage']:.2f}%\n\n"
            )

            report.write(
                "### Automated Insights\n\n"
            )

            for insight in result["insights"]:

                report.write(
                    f"**{insight['category']}**\n\n"
                )

                report.write(
                    f"- Finding: "
                    f"{insight['finding']}\n"
                )

                report.write(
                    f"- Evidence: "
                    f"{insight['evidence']}\n"
                )

                report.write(
                    f"- Recommendation: "
                    f"{insight['recommendation']}\n\n"
                )

        report.write(
            "## Limitations\n\n"
        )

        report.write(
            "- Anomalies indicate unusual observations, "
            "not confirmed business problems.\n"
            "- Correlation does not establish causation.\n"
            "- Automated insights should be validated by "
            "a human analyst.\n"
            "- Results depend on dataset quality and "
            "completeness.\n"
        )

    print(
        f"\nReport created: {report_path}"
    )


def main():

    ensure_directories()

    results = {}

    sales_file = DATA_DIR / "sales.csv"
    support_file = DATA_DIR / "support.csv"

    if sales_file.exists():

        results["sales"] = analyze_dataset(
            sales_file,
            "sales"
        )

    else:

        print(
            f"Warning: {sales_file} not found."
        )

    if support_file.exists():

        results["support"] = analyze_dataset(
            support_file,
            "support"
        )

    else:

        print(
            f"Warning: {support_file} not found."
        )

    if not results:

        raise FileNotFoundError(
            "No CSV files found in the data directory."
        )

    build_summary(results)

    build_report(results)

    print("\n" + "=" * 60)
    print(
        "DATA DETECTIVE AI ANALYSIS COMPLETE"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()