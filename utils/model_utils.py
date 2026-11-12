
import json
import joblib
import pandas as pd
import streamlit as st

from config import (
    MODEL_PATH,
    METADATA_PATH,
    CUSTOMER_DATA_PATH
)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metadata():
    with open(METADATA_PATH, "r") as file:
        return json.load(file)


@st.cache_data
def load_customer_data():
    df = pd.read_csv(CUSTOMER_DATA_PATH)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    return df


@st.cache_data
def generate_customer_risk():
    df = load_customer_data()
    metadata = load_metadata()
    model = load_model()

    latest_date = df["snapshot_date"].max()

    latest_df = df[
        df["snapshot_date"] == latest_date
    ].copy()

    feature_columns = (
        metadata["numerical_features"]
        + metadata["categorical_features"]
    )

    missing_columns = [
        col for col in feature_columns
        if col not in latest_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing model features: {missing_columns}"
        )

    X = latest_df[feature_columns]

    scores = model.predict_proba(X)[:, 1]

    latest_df["churn_score"] = scores

    latest_df["risk_segment"] = pd.qcut(
        latest_df["churn_score"].rank(method="first"),
        q=3,
        labels=["Low", "Medium", "High"]
    )

    latest_df["risk_segment"] = (
        latest_df["risk_segment"].astype(str)
    )

    latest_df["churn_prediction"] = (
        latest_df["churn_score"]
        >= metadata["classification_threshold"]
    ).astype(int)

    return latest_df, metadata
