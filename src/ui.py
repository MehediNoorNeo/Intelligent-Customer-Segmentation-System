"""Escaped, reusable semantic HTML for dashboard sections."""

from html import escape
from pathlib import Path
from string import Template

import streamlit as st

from charts import COLORS


TEMPLATES = Path(__file__).resolve().parent / "templates"
SEGMENT_DESCRIPTIONS = {
    0: "Visits the web often while making fewer purchases and keeping spending modest.",
    1: "Has the longest tenure and makes the most store purchases, with the highest average spending.",
    2: "Makes the most deal purchases and has the most children at home on average, with modest spending.",
    3: "Buys across web, catalog, and stores, with high average income and spending.",
}


def render(name: str, **values: object) -> None:
    source = (TEMPLATES / name).read_text(encoding="utf-8")
    st.html(Template(source).substitute({key: escape(str(value)) for key, value in values.items()}))


def metric_grid(metrics: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        '<article class="rounded-2xl border border-slate-700 bg-slate-800 px-5 py-5 shadow-sm">'
        f'<p class="m-0 text-xs font-semibold uppercase tracking-wider text-slate-300">{escape(label)}</p>'
        f'<p class="my-2 text-3xl font-bold tracking-tight text-slate-100">{escape(value)}</p>'
        f'<p class="m-0 text-sm text-slate-400">{escape(note)}</p></article>'
        for label, value, note in metrics
    )
    st.html(f'<section aria-label="Portfolio key metrics" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">{cards}</section>')


def segment_cards(profiles, portfolio) -> None:
    cards = []
    for row in profiles.itertuples():
        share = row.Customers / len(portfolio) * 100
        description = SEGMENT_DESCRIPTIONS[row.Cluster]
        color = COLORS[row.Segment]
        cards.append(
            '<article class="rounded-2xl border border-slate-700 bg-slate-800 p-5 shadow-sm">'
            '<div class="mb-4 flex items-center gap-3">'
            f'<span aria-hidden="true" class="h-3 w-3 rounded-full" style="background:{color}"></span>'
            f'<h3 class="m-0 text-base font-bold text-slate-100">{escape(row.Segment)}</h3>'
            f'<span class="ml-auto text-sm font-semibold text-slate-300">{share:.1f}%</span></div>'
            f'<p class="mb-4 min-h-16 text-sm leading-6 text-slate-300">{escape(description)}</p>'
            '<div class="flex justify-between border-t border-slate-700 pt-3 text-sm">'
            f'<span class="text-slate-400">{row.Customers:,.0f} customers</span>'
            f'<strong class="text-slate-100">{row.Mean_Spending:,.0f} avg. spend</strong></div></article>'
        )
    st.html('<section aria-label="Segment profiles" class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">' + "".join(cards) + '</section>')


def section_heading(kicker: str, title: str, description: str) -> None:
    st.html(
        '<header class="mb-5 mt-10">'
        f'<p class="mb-2 text-xs font-bold uppercase tracking-widest text-teal-300">{escape(kicker)}</p>'
        f'<h2 class="m-0 text-2xl font-bold tracking-tight text-slate-100">{escape(title)}</h2>'
        f'<p class="mb-0 mt-2 max-w-3xl text-sm leading-6 text-slate-300">{escape(description)}</p>'
        '</header>'
    )
