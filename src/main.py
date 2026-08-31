import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ------------------------------------------------------------
# IMPORT EXISTING PROJECT FUNCTIONS
# ------------------------------------------------------------

from src.analyzer import (
    get_data_quality,
    get_numeric_summary,
    get_categorical_summary,
    calculate_business_metrics,
)

from src.anomaly_detector import (
    detect_anomalies,
    get_anomaly_summary,
    get_top_anomalies,
)

from src.data_cleaner import (
    clean_dataset,
    generate_quality_report,
)

from src.data_loader import (
    load_file,
    get_dataset_info,
)

from src.profiler import profile_dataframe

from src.visualizer import (
    plot_missing_values,
    plot_numeric_distribution,
    plot_time_series,
    plot_category_performance,
    plot_anomalies,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Data Detective AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            #f8fafc,
            #eef2ff
        );
        border: 1px solid #e5e7eb;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin-bottom: 5px;
    }

    .hero p {
        color: #4b5563;
        font-size: 16px;
    }

    .metric-card {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        padding: 25px;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

    <h1>🔎 Data Detective AI</h1>

    <p>
    Automated business data investigation platform for
    profiling, data quality analysis, anomaly detection,
    KPI analysis and business insights.
    </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Data Detective AI")

st.sidebar.markdown(
    """
    ### Investigation Pipeline

    1. Upload data
    2. Data profiling
    3. Data quality
    4. Anomaly detection
    5. Business metrics
    6. Visual analysis
    7. Business insights
    """
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx", "xls"],
)


# ============================================================
# DEMO DATA OPTION
# ============================================================

use_demo_data = st.sidebar.checkbox(
    "Use sample sales data"
)


# ============================================================
# LOAD DATA
# ============================================================

df = None
file_name = None


if uploaded_file is not None:

    file_name = uploaded_file.name

    try:

        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("Dataset loaded successfully.")

    except Exception as e:

        st.sidebar.error(
            f"Unable to load file: {e}"
        )


elif use_demo_data:

    demo_path = PROJECT_ROOT / "data" / "sales.csv"

    if demo_path.exists():

        try:

            df = pd.read_csv(demo_path)
            file_name = "sales.csv"

            st.sidebar.success(
                "Demo sales dataset loaded."
            )

        except Exception as e:

            st.sidebar.error(
                f"Could not load demo data: {e}"
            )

    else:

        st.sidebar.warning(
            "data/sales.csv was not found."
        )


# ============================================================
# NO DATA SCREEN
# ============================================================

if df is None:

    st.info(
        "Upload a CSV/Excel dataset from the sidebar "
        "or select **Use sample sales data**."
    )

    st.markdown("### What this project does")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Data Profiling",
            "Automated"
        )

    with col2:
        st.metric(
            "Quality Checks",
            "Automated"
        )

    with col3:
        st.metric(
            "Anomaly Detection",
            "Enabled"
        )

    with col4:
        st.metric(
            "Business Analysis",
            "Enabled"
        )

    st.stop()


# ============================================================
# BASIC DATA PREPARATION
# ============================================================

df = df.copy()

# Try cleaning safely
try:

    cleaned_df = clean_dataset(
        df.copy()
    )

    if isinstance(cleaned_df, pd.DataFrame):

        df_analysis = cleaned_df

    else:

        df_analysis = df

except Exception:

    df_analysis = df


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.header("Dataset Overview")

rows = len(df_analysis)
columns = len(df_analysis.columns)

missing_values = int(
    df_analysis.isna().sum().sum()
)

duplicate_rows = int(
    df_analysis.duplicated().sum()
)

numeric_columns = len(
    df_analysis.select_dtypes(
        include="number"
    ).columns
)

categorical_columns = len(
    df_analysis.select_dtypes(
        include=["object", "category"]
    ).columns
)


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Rows",
        f"{rows:,}"
    )

with col2:
    st.metric(
        "Columns",
        columns
    )

with col3:
    st.metric(
        "Missing Values",
        f"{missing_values:,}"
    )

with col4:
    st.metric(
        "Duplicates",
        f"{duplicate_rows:,}"
    )

with col5:
    st.metric(
        "Numeric Columns",
        numeric_columns
    )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Dataset",
        "Profile",
        "Data Quality",
        "Anomalies",
        "Business Analysis",
        "Visualizations",
    ]
)


# ============================================================
# TAB 1 — DATASET
# ============================================================

with tab1:

    st.subheader("Data Preview")

    st.dataframe(
        df_analysis.head(100),
        use_container_width=True,
    )

    st.subheader("Column Information")

    column_info = pd.DataFrame(
        {
            "Column": df_analysis.columns,
            "Data Type": [
                str(dtype)
                for dtype in df_analysis.dtypes
            ],
            "Missing": [
                int(df_analysis[col].isna().sum())
                for col in df_analysis.columns
            ],
            "Unique Values": [
                int(df_analysis[col].nunique())
                for col in df_analysis.columns
            ],
        }
    )

    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# TAB 2 — PROFILE
# ============================================================

with tab2:

    st.subheader("Automated Data Profile")

    try:

        profile = profile_dataframe(
            df_analysis
        )

        if isinstance(profile, dict):

            for key, value in profile.items():

                st.write(
                    f"**{key}:** {value}"
                )

        elif isinstance(profile, pd.DataFrame):

            st.dataframe(
                profile,
                use_container_width=True,
            )

        else:

            st.write(profile)

    except Exception as e:

        st.warning(
            f"Profiling could not be displayed: {e}"
        )

    st.subheader("Numeric Summary")

    try:

        numeric_summary = get_numeric_summary(
            df_analysis
        )

        if numeric_summary is not None:

            st.dataframe(
                numeric_summary,
                use_container_width=True,
            )

    except Exception as e:

        st.warning(
            f"Numeric summary unavailable: {e}"
        )

    st.subheader("Categorical Summary")

    try:

        categorical_summary = get_categorical_summary(
            df_analysis
        )

        if categorical_summary is not None:

            st.dataframe(
                categorical_summary,
                use_container_width=True,
            )

    except Exception as e:

        st.warning(
            f"Categorical summary unavailable: {e}"
        )


# ============================================================
# TAB 3 — DATA QUALITY
# ============================================================

with tab3:

    st.subheader("Data Quality Assessment")

    try:

        quality = get_data_quality(
            df_analysis
        )

        if isinstance(quality, dict):

            quality_df = pd.DataFrame(
                [
                    {
                        "Metric": key,
                        "Value": value,
                    }
                    for key, value in quality.items()
                ]
            )

            st.dataframe(
                quality_df,
                use_container_width=True,
                hide_index=True,
            )

        elif isinstance(quality, pd.DataFrame):

            st.dataframe(
                quality,
                use_container_width=True,
            )

        else:

            st.write(quality)

    except Exception as e:

        st.error(
            f"Data quality analysis failed: {e}"
        )

    st.subheader("Missing Values")

    missing = (
        df_analysis.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    missing = missing[
        missing > 0
    ]

    if len(missing) == 0:

        st.success(
            "No missing values detected."
        )

    else:

        missing_df = (
            missing
            .reset_index()
        )

        missing_df.columns = [
            "Column",
            "Missing Values",
        ]

        st.dataframe(
            missing_df,
            use_container_width=True,
            hide_index=True,
        )

        try:

            fig = plot_missing_values(
                df_analysis
            )

            if fig is not None:
                st.pyplot(fig)

        except Exception:

            pass


# ============================================================
# TAB 4 — ANOMALIES
# ============================================================

with tab4:

    st.subheader(
        "Automated Anomaly Detection"
    )

    try:

        anomaly_df = detect_anomalies(
            df_analysis
        )

        if isinstance(anomaly_df, pd.DataFrame):

            st.write(
                f"Detected **{len(anomaly_df):,}** "
                "potential anomalous records."
            )

            st.dataframe(
                anomaly_df.head(50),
                use_container_width=True,
            )

            try:

                summary = get_anomaly_summary(
                    anomaly_df
                )

                if summary is not None:

                    st.subheader(
                        "Anomaly Summary"
                    )

                    if isinstance(
                        summary,
                        pd.DataFrame
                    ):

                        st.dataframe(
                            summary,
                            use_container_width=True,
                        )

                    else:

                        st.write(summary)

            except Exception:

                pass

            try:

                top_anomalies = get_top_anomalies(
                    anomaly_df
                )

                if top_anomalies is not None:

                    st.subheader(
                        "Top Anomalies"
                    )

                    st.dataframe(
                        top_anomalies,
                        use_container_width=True,
                    )

            except Exception:

                pass

        else:

            st.info(
                "No anomaly table was returned."
            )

    except Exception as e:

        st.warning(
            f"Anomaly detection could not run: {e}"
        )


# ============================================================
# TAB 5 — BUSINESS ANALYSIS
# ============================================================

with tab5:

    st.subheader(
        "Business Metrics"
    )

    try:

        metrics = calculate_business_metrics(
            df_analysis
        )

        if isinstance(metrics, dict):

            metric_cols = st.columns(
                min(
                    len(metrics),
                    4
                )
            )

            for index, (
                metric_name,
                metric_value
            ) in enumerate(
                metrics.items()
            ):

                with metric_cols[
                    index % len(metric_cols)
                ]:

                    st.metric(
                        str(metric_name),
                        str(metric_value)
                    )

        elif isinstance(
            metrics,
            pd.DataFrame
        ):

            st.dataframe(
                metrics,
                use_container_width=True,
            )

        else:

            st.write(metrics)

    except Exception as e:

        st.warning(
            f"Business metrics unavailable: {e}"
        )

    st.subheader(
        "Numeric Relationships"
    )

    numeric_cols = list(
        df_analysis.select_dtypes(
            include="number"
        ).columns
    )

    if len(numeric_cols) >= 2:

        correlation = (
            df_analysis[numeric_cols]
            .corr(numeric_only=True)
        )

        st.dataframe(
            correlation,
            use_container_width=True,
        )

    else:

        st.info(
            "At least two numeric columns "
            "are required for correlation analysis."
        )


# ============================================================
# TAB 6 — VISUALIZATIONS
# ============================================================

with tab6:

    st.subheader(
        "Automated Business Visualizations"
    )

    numeric_cols = list(
        df_analysis.select_dtypes(
            include="number"
        ).columns
    )

    categorical_cols = list(
        df_analysis.select_dtypes(
            include=[
                "object",
                "category"
            ]
        ).columns
    )

    # --------------------------------------------------------
    # Numeric distribution
    # --------------------------------------------------------

    if numeric_cols:

        selected_numeric = st.selectbox(
            "Select numeric column",
            numeric_cols,
        )

        try:

            fig = plot_numeric_distribution(
                df_analysis,
                selected_numeric,
            )

            if fig is not None:
                st.pyplot(fig)

        except TypeError:

            try:

                fig = plot_numeric_distribution(
                    df_analysis
                )

                if fig is not None:
                    st.pyplot(fig)

            except Exception as e:

                st.warning(
                    f"Distribution chart unavailable: {e}"
                )

        except Exception as e:

            st.warning(
                f"Distribution chart unavailable: {e}"
            )

    # --------------------------------------------------------
    # Category analysis
    # --------------------------------------------------------

    if categorical_cols and numeric_cols:

        st.subheader(
            "Category Performance"
        )

        category = st.selectbox(
            "Category column",
            categorical_cols,
            key="category_column",
        )

        metric = st.selectbox(
            "Metric column",
            numeric_cols,
            key="metric_column",
        )

        try:

            fig = plot_category_performance(
                df_analysis,
                category,
                metric,
            )

            if fig is not None:
                st.pyplot(fig)

        except Exception as e:

            st.warning(
                f"Category chart unavailable: {e}"
            )


# ============================================================
# FINAL DATA TABLE
# ============================================================

st.divider()

st.subheader("Analysis Dataset")

st.caption(
    f"Source: {file_name} | "
    f"{rows:,} rows × {columns} columns"
)

st.dataframe(
    df_analysis,
    use_container_width=True,
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

    <strong>Data Detective AI | RetailIQ Business Analytics</strong>
    <br><br>

    Automated profiling |
    Data quality analysis |
    Anomaly detection |
    Business metrics |
    Visual analytics

    <br><br>

    Built with Python, Pandas, Streamlit and Scikit-learn

    </div>
    """,
    unsafe_allow_html=True,
)