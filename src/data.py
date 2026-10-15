"""Data and fitted model access for the SmartSeg dashboard."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "smartcart_customers_cleaned.csv"
MODELS = ROOT / "models"
FEATURES = [
    "Income", "Recency", "NumDealsPurchases", "NumWebPurchases",
    "NumCatalogPurchases", "NumStorePurchases", "NumWebVisitsMonth",
    "Age", "Customer_Tenure", "Total_Spending", "Total_Children",
    "Education_Graduate", "Education_Postgraduate", "Education_Undergraduate",
    "Marital_Status_Partner", "Marital_Status_Previously_Married",
    "Marital_Status_Single", "Marital_Status_Unknown",
]
SEGMENT_NAMES = {
    0: "Selective Value Shoppers",
    1: "Established Premium Buyers",
    2: "Deal-Seeking Family Shoppers",
    3: "Affluent Multi-Channel Shoppers",
}
SEGMENTS = list(SEGMENT_NAMES.values())


def segment_name(cluster: int) -> str:
    return SEGMENT_NAMES[cluster]


@st.cache_resource
def _load_assets():
    data = pd.read_csv(DATA_PATH)
    missing = set(FEATURES) - set(data.columns)
    if missing:
        raise ValueError(f"Processed data is missing columns: {', '.join(sorted(missing))}")
    data = data[FEATURES].copy()
    scaler = joblib.load(MODELS / "standard_scaler.pkl")
    pca = joblib.load(MODELS / "pca.pkl")
    model = joblib.load(MODELS / "kmeans_model.pkl")
    projected = pca.transform(scaler.transform(data))
    data["Cluster"] = model.predict(projected)
    data["PC1"] = projected[:, 0]
    data["PC2"] = projected[:, 1]
    return data, scaler, pca, model


def load_assets():
    """Return current segment labels without mutating the cached model data."""
    cached_data, scaler, pca, model = _load_assets()
    data = cached_data.copy()
    data["Segment"] = data["Cluster"].map(segment_name)
    return data, scaler, pca, model


def build_profiles(customers: pd.DataFrame) -> pd.DataFrame:
    return (
        customers.groupby(["Cluster", "Segment"], as_index=False)
        .agg(
            Customers=("Income", "size"),
            Mean_Income=("Income", "mean"),
            Mean_Spending=("Total_Spending", "mean"),
            Mean_Web_Visits=("NumWebVisitsMonth", "mean"),
            Mean_Web_Purchases=("NumWebPurchases", "mean"),
            Mean_Catalog_Purchases=("NumCatalogPurchases", "mean"),
            Mean_Store_Purchases=("NumStorePurchases", "mean"),
            Mean_Deals=("NumDealsPurchases", "mean"),
            Mean_Age=("Age", "mean"),
            Mean_Children=("Total_Children", "mean"),
        )
        .sort_values("Cluster")
    )
