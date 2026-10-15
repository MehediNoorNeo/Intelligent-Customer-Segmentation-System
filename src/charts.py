"""Plotly figures with shared dashboard styling."""

import plotly.express as px

from data import SEGMENTS


COLORS = dict(zip(SEGMENTS, ["#53D7C8", "#93A5FF", "#F0B35C", "#E89BBB"]))
CHART_CONFIG = {"displayModeBar": False, "responsive": True}


def style(fig, height=350, showlegend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=14, t=22, b=10),
        paper_bgcolor="#1E293B",
        plot_bgcolor="#1E293B",
        font=dict(color="#D5E1F0", family="Arial, sans-serif", size=12),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, x=0),
        showlegend=showlegend,
        hoverlabel=dict(bgcolor="#0B1424", font_color="#F7FAFF", font_size=12),
    )
    fig.update_xaxes(gridcolor="#34445C", linecolor="#496078", zeroline=False, automargin=True, title_standoff=12)
    fig.update_yaxes(gridcolor="#34445C", linecolor="#496078", zeroline=False, automargin=True, title_standoff=12)
    return fig


def landscape(customers):
    fig = px.scatter(
        customers, x="Total_Spending", y="Income", color="Segment",
        color_discrete_map=COLORS, category_orders={"Segment": SEGMENTS},
        hover_data={"Age": True, "Recency": True, "Total_Spending": ":,.0f", "Income": ":,.0f"},
        opacity=0.64,
        labels={"Total_Spending": "Total spending (source units)", "Income": "Income (source units)"},
    )
    fig.update_traces(marker=dict(size=7, line=dict(width=0)))
    return style(fig, 390)


def size_bars(profiles):
    fig = px.bar(
        profiles, x="Customers", y="Segment", color="Segment", text="Customers",
        orientation="h",
        color_discrete_map=COLORS, category_orders={"Segment": SEGMENTS},
        labels={"Customers": "Customers", "Segment": ""},
    )
    fig.update_traces(textposition="outside", textfont_color="#F7FAFF", cliponaxis=False)
    fig.update_xaxes(rangemode="tozero")
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(SEGMENTS)))
    return style(fig, 390, False)


def pca_scatter(customers):
    fig = px.scatter(
        customers, x="PC1", y="PC2", color="Segment", opacity=0.62,
        color_discrete_map=COLORS, category_orders={"Segment": SEGMENTS},
        labels={"PC1": "Principal component 1", "PC2": "Principal component 2"},
        hover_data={"Income": ":,.0f", "Total_Spending": ":,.0f", "PC1": False, "PC2": False},
    )
    fig.update_traces(marker=dict(size=6, line=dict(width=0)))
    return style(fig, 390)


def comparison(profiles):
    comparison_data = profiles.melt(
        id_vars="Segment", value_vars=["Mean_Income", "Mean_Spending"],
        var_name="Measure", value_name="Average",
    )
    comparison_data["Measure"] = comparison_data["Measure"].map({
        "Mean_Income": "Income", "Mean_Spending": "Spending",
    })
    fig = px.bar(
        comparison_data, x="Average", y="Segment", color="Segment", facet_col="Measure",
        orientation="h", color_discrete_map=COLORS,
        category_orders={"Segment": list(reversed(SEGMENTS)), "Measure": ["Income", "Spending"]},
        labels={"Average": "Average (source units)", "Segment": ""},
    )
    fig.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
    fig.update_xaxes(tickformat=",.0f")
    fig.update_xaxes(matches=None)
    return style(fig, 390, False)
