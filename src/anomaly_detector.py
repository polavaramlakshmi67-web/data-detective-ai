import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

from src.analyzer import prepare_numeric_data


def detect_anomalies(
    df,
    contamination="auto",
    random_state=42
):
    """
    Detect anomalies using Isolation Forest.

    Returns the original dataset with:
    - anomaly_score
    - anomaly_label
    - is_anomaly
    """
    numeric_df = prepare_numeric_data(df)

    if numeric_df.empty:
        result = df.copy()
        result["anomaly_score"] = np.nan
        result["anomaly_label"] = "Not Available"
        result["is_anomaly"] = False
        return result

    if len(numeric_df) < 5:
        result = df.copy()
        result["anomaly_score"] = np.nan
        result["anomaly_label"] = "Not Enough Data"
        result["is_anomaly"] = False
        return result

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=200
    )

    predictions = model.fit_predict(numeric_df)

    scores = model.decision_function(numeric_df)

    result = df.copy()

    result["anomaly_score"] = scores

    result["anomaly_label"] = np.where(
        predictions == -1,
        "Anomaly",
        "Normal"
    )

    result["is_anomaly"] = predictions == -1

    return result


def get_anomaly_summary(anomaly_df):
    """
    Return anomaly statistics.
    """
    total = len(anomaly_df)

    if "is_anomaly" not in anomaly_df.columns:
        return {
            "total_records": total,
            "anomalies": 0,
            "anomaly_percentage": 0.0,
        }

    anomalies = int(anomaly_df["is_anomaly"].sum())

    percentage = (
        anomalies / total * 100
        if total > 0
        else 0
    )

    return {
        "total_records": total,
        "anomalies": anomalies,
        "normal_records": total - anomalies,
        "anomaly_percentage": round(percentage, 2),
    }


def get_top_anomalies(anomaly_df, n=10):
    """
    Return the strongest anomalies.
    Lower Isolation Forest decision scores indicate more unusual records.
    """
    if "anomaly_score" not in anomaly_df.columns:
        return pd.DataFrame()

    anomalies = anomaly_df[
        anomaly_df["is_anomaly"] == True
    ].copy()

    return anomalies.sort_values(
        "anomaly_score",
        ascending=True
    ).head(n)