"""SmartSeg customer segmentation dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

from charts import CHART_CONFIG, comparison, landscape, pca_scatter, size_bars
from data import FEATURES, SEGMENTS, build_profiles, load_assets, segment_name
from ui import metric_grid, render, section_heading, segment_cards


SRC = Path(__file__).resolve().parent


def customer_input(data: pd.DataFrame) -> pd.DataFrame | None:
    medians = data[FEATURES].median()
    with st.form("segment_prediction"):
        st.markdown("#### Customer details")
        a, b, c = st.columns(3, gap="large")
        with a:
            income = st.number_input("Income (source units)", min_value=0.0, value=float(round(medians["Income"])), step=1000.0)
            spending = st.number_input("Total spending (source units)", min_value=0.0, value=float(round(medians["Total_Spending"])), step=50.0)
            recency = st.number_input("Days since last purchase", min_value=0, value=int(medians["Recency"]), step=1)
            age = st.number_input("Age (years)", min_value=18, max_value=90, value=int(medians["Age"]), step=1)
        with b:
            web = st.number_input("Web purchases", min_value=0, value=int(medians["NumWebPurchases"]), step=1)
            catalog = st.number_input("Catalog purchases", min_value=0, value=int(medians["NumCatalogPurchases"]), step=1)
            store = st.number_input("Store purchases", min_value=0, value=int(medians["NumStorePurchases"]), step=1)
            deals = st.number_input("Deal purchases", min_value=0, value=int(medians["NumDealsPurchases"]), step=1)
        with c:
            visits = st.number_input("Monthly web visits", min_value=0, value=int(medians["NumWebVisitsMonth"]), step=1)
            tenure = st.number_input("Customer tenure (days)", min_value=0, value=int(medians["Customer_Tenure"]), step=1)
            children = st.number_input("Children at home", min_value=0, value=int(medians["Total_Children"]), step=1)
            education = st.selectbox("Education", ["Graduate", "Postgraduate", "Undergraduate"])
            marital = st.selectbox("Marital status", ["Partner", "Previously Married", "Single", "Unknown"])
        submitted = st.form_submit_button("Find customer segment", type="primary", width="stretch")

    if not submitted:
        return None
    values = {
        "Income": income, "Recency": recency, "NumDealsPurchases": deals,
        "NumWebPurchases": web, "NumCatalogPurchases": catalog,
        "NumStorePurchases": store, "NumWebVisitsMonth": visits,
        "Age": age, "Customer_Tenure": tenure,
        "Total_Spending": spending, "Total_Children": children,
        f"Education_{education}": 1,
        f"Marital_Status_{marital.replace(' ', '_')}": 1,
    }
    return pd.DataFrame([{feature: values.get(feature, 0) for feature in FEATURES}])


st.set_page_config(page_title="SmartSeg | Customer intelligence", page_icon="◈", layout="wide")
st.html(SRC / "styles" / "tailwind.css")
st.html(SRC / "styles" / "main.css")

try:
    customers, scaler, pca, model = load_assets()
except (FileNotFoundError, ValueError, ImportError) as exc:
    st.error(f"The dashboard could not load its data or model: {exc}")
    st.stop()

profiles = build_profiles(customers)
render("hero.html", customers=f"{len(customers):,}")

area = st.segmented_control(
    "Dashboard area", ["Overview", "Explore segments", "Predict a segment"],
    default="Overview", key="dashboard_area", label_visibility="visible",
)

if area == "Overview":
    section_heading("Portfolio at a glance", "Customer overview", "A concise view of customer size, purchasing, and the four fitted groups.")
    metric_grid([
        ("Customers analyzed", f"{len(customers):,}", "Cleaned customer records"),
        ("Customer segments", str(model.n_clusters), "KMeans groups; IDs are not ranks"),
        ("Median total spending", f"{customers['Total_Spending'].median():,.0f}", "Source dataset units"),
        ("Average income", f"{customers['Income'].mean():,.0f}", "Source dataset units"),
    ])

    section_heading("Distribution", "Customer landscape", "Compare individual income and spending with the relative size of each segment.")
    left, right = st.columns([1.45, 1], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("#### Income and total spending")
            st.plotly_chart(landscape(customers), width="stretch", config=CHART_CONFIG)
            st.caption("Each dot is one customer. Color identifies a segment; axes use source dataset units.")
    with right:
        with st.container(border=True):
            st.markdown("#### Customers in each segment")
            st.plotly_chart(size_bars(profiles), width="stretch", config=CHART_CONFIG)
            st.caption("Bar height shows the number of customers assigned to each model group.")

    section_heading("Profiles", "Meet the customer groups", "Each name highlights a pattern in the group's average shopping behavior.")
    segment_cards(profiles, customers)

if area == "Explore segments":
    section_heading("Segment explorer", "Compare customer groups", "Choose groups to update the charts and table. All figures are descriptive, based on the fitted model and processed data.")
    selected = st.multiselect("Show segments", SEGMENTS, default=SEGMENTS, help="Select one or more model groups to compare.")
    if not selected:
        st.info("Select at least one segment to view the charts and table.")
    else:
        visible = customers[customers["Segment"].isin(selected)]
        selected_profiles = profiles[profiles["Segment"].isin(selected)]
        c1, c2 = st.columns([1.15, 1], gap="large")
        with c1:
            with st.container(border=True):
                st.markdown("#### Model map")
                st.plotly_chart(pca_scatter(visible), width="stretch", config=CHART_CONFIG)
                st.caption("Each dot is a customer projected onto the first two principal components. The model uses three components.")
        with c2:
            with st.container(border=True):
                st.markdown("#### Average income and spending")
                st.plotly_chart(comparison(selected_profiles), width="stretch", config=CHART_CONFIG)
                st.caption("Separate scales show average income and total spending in source dataset units.")

        section_heading("Detail", "Segment summary", "Compare group size, purchasing, and web activity. Download the selected customer records for further analysis.")
        summary = selected_profiles.rename(columns={
            "Mean_Income": "Mean income", "Mean_Spending": "Mean spending",
            "Mean_Web_Visits": "Mean monthly web visits", "Mean_Web_Purchases": "Mean web purchases",
            "Mean_Store_Purchases": "Mean store purchases",
        })[["Segment", "Customers", "Mean income", "Mean spending", "Mean monthly web visits", "Mean web purchases", "Mean store purchases"]]
        st.dataframe(summary.style.format({
            "Mean income": "{:,.0f}", "Mean spending": "{:,.0f}",
            "Mean monthly web visits": "{:.1f}", "Mean web purchases": "{:.1f}",
            "Mean store purchases": "{:.1f}",
        }), hide_index=True, width="stretch")
        st.download_button(
            "Download selected customers as CSV",
            data=visible.drop(columns=["PC1", "PC2"]).to_csv(index=False),
            file_name="smartseg_customers.csv", mime="text/csv",
        )

if area == "Predict a segment":
    section_heading("Classification", "Find a customer's segment", "Enter a profile to assign it to the closest fitted group. Start with typical values and adjust what you know.")
    sample = customer_input(customers)
    if sample is not None:
        cluster = int(model.predict(pca.transform(scaler.transform(sample)))[0])
        st.session_state["prediction_cluster"] = cluster
    if "prediction_cluster" in st.session_state:
        cluster = st.session_state["prediction_cluster"]
        profile = profiles.loc[profiles["Cluster"] == cluster].iloc[0]
        render("result_card.html", segment=segment_name(cluster), customers=f"{int(profile['Customers']):,}",
               income=f"{profile['Mean_Income']:,.0f}", spending=f"{profile['Mean_Spending']:,.0f}")
        st.caption("This is similarity based grouping, not a forecast of future spending or income. Income and spending use source dataset units.")

st.html('<footer class="mt-12 border-t border-slate-700 py-6 text-center text-xs text-slate-400">SmartSeg · Exploratory customer segmentation · Based on processed customer data and saved model artifacts</footer>')
