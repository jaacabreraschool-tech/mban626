import os
from urllib.parse import quote_plus

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

TICKET_FILE = "tickets.csv"
HEADERS = [
    "Ticket Number",
    "Name",
    "Priority",
    "Assigned To",
    "Product Purchased",
    "Date of Purchase",
    "Type",
    "Short Description",
    "Detailed Description",
]
PRIORITIES = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
PRIORITY_SHORT = ["P1", "P2", "P3", "P4"]
TIERS = ["Tier 1 Support", "Tier 2 Support"]


def show_details_page(assignee: str | None, priority: str | None) -> None:
    """Render the assignment drilldown page from query-string filters."""
    st.title("Tickets Assignment Details")
    st.markdown("List of tickets for the selected breakdown link")
    st.markdown("---")

    df = load_tickets()
    if len(df) == 0:
        st.warning("No tickets found.")
        if st.button("Back to Dashboard"):
            st.query_params.clear()
            st.rerun()
        return

    filtered = df.copy()
    if assignee and assignee.lower() != "all":
        filtered = filtered[filtered["Assigned To"] == assignee]
    if priority and priority.lower() != "all":
        filtered = filtered[filtered["Priority"] == priority]

    assignee_label = assignee if assignee and assignee.lower() != "all" else "All Assignees"
    priority_label = priority if priority and priority.lower() != "all" else "All Priorities"

    st.markdown(f"**Assignee**: {assignee_label}")
    st.markdown(f"**Priority**: {priority_label}")
    st.markdown(f"**Tickets Found**: {len(filtered)}")
    st.dataframe(filtered, hide_index=True, width="stretch")

    if st.button("Back to Dashboard"):
        st.query_params.clear()
        st.rerun()


def load_tickets() -> pd.DataFrame:
    """Load ticket data from CSV, returning an empty frame if missing."""
    if os.path.exists(TICKET_FILE):
        df = pd.read_csv(TICKET_FILE)
        if len(df) > 0:
            return df
    return pd.DataFrame(columns=HEADERS)


def show() -> None:
    st.title("Tickets Assignments")
    st.markdown("Tier 1 vs Tier 2 Support distribution by priority")
    st.markdown("---")

    df = load_tickets()
    if len(df) == 0:
        st.warning("No tickets yet. Submit tickets to see assignment reports.")
        return

    breakdown = {}
    for tier in TIERS:
        breakdown[tier] = {}
        for short_p, full_p in zip(PRIORITY_SHORT, PRIORITIES):
            count = len(df[(df["Priority"] == full_p) & (df["Assigned To"] == tier)])
            breakdown[tier][short_p] = count

    tier1_counts = np.array([breakdown["Tier 1 Support"][p] for p in PRIORITY_SHORT])
    tier2_counts = np.array([breakdown["Tier 2 Support"][p] for p in PRIORITY_SHORT])

    tier1_total = int(np.sum(tier1_counts))
    tier2_total = int(np.sum(tier2_counts))
    grand_total = tier1_total + tier2_total

    col1, col2, col3 = st.columns(3)
    with col1:
        delta = f"{(tier1_total / grand_total * 100):.1f}%" if grand_total else "0.0%"
        st.metric("Tier 1 Support", tier1_total, delta=delta)
    with col2:
        delta = f"{(tier2_total / grand_total * 100):.1f}%" if grand_total else "0.0%"
        st.metric("Tier 2 Support", tier2_total, delta=delta)
    with col3:
        st.metric("Total Tickets", grand_total)

    st.markdown("---")
    st.markdown("### Priority Distribution")

    left_col, right_col = st.columns(2)
    for idx, short_p in enumerate(PRIORITY_SHORT):
        target_col = left_col if idx % 2 == 0 else right_col
        with target_col:
            st.markdown(f"**{short_p}**")
            t1_val = breakdown["Tier 1 Support"][short_p]
            t2_val = breakdown["Tier 2 Support"][short_p]
            total_val = t1_val + t2_val

            if total_val == 0:
                st.info(f"No tickets for {short_p}")
                continue

            fig, ax = plt.subplots(figsize=(3.0, 2.6), dpi=110)
            sizes = [t1_val, t2_val]
            labels = ["Tier 1", "Tier 2"]
            colors = ["#1f77b4", "#d62728"]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                colors=colors,
                startangle=90,
                radius=0.84,
                textprops={"fontsize": 8, "fontweight": "bold"},
            )
            for autotext in autotexts:
                autotext.set_color("white")

            ax.set_title(f"{short_p} Priority", fontsize=9, fontweight="bold")
            st.pyplot(fig, use_container_width=False)
            st.caption(f"Tier 1: {t1_val} | Tier 2: {t2_val} | Total: {total_val}")

    st.markdown("---")
    st.markdown("### Breakdown by Assignee")
    st.caption("Click any number to open a details page with matching tickets.")

    def build_link(value: int, assignee: str | None, priority: str | None) -> str:
        params = ["view=assignment-details"]
        if assignee is not None:
            params.append(f"assignee={quote_plus(assignee)}")
        else:
            params.append("assignee=all")

        if priority is not None:
            params.append(f"priority={quote_plus(priority)}")
        else:
            params.append("priority=all")

        href = "?" + "&".join(params)
        return f'<a href="{href}" target="_self">{value}</a>'

    table_style = """
    <style>
    .assignment-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .assignment-table th { background: #f2f4f8; padding: 10px; text-align: center; }
    .assignment-table td { border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: center; }
    .assignment-table td:first-child, .assignment-table th:first-child { text-align: left; }
    .assignment-table a { color: #1e3a8a; font-weight: 700; text-decoration: underline; }
    .assignment-table tr:last-child td { font-weight: 700; }
    </style>
    """
    st.markdown(table_style, unsafe_allow_html=True)

    header = "<tr><th>ASSIGNEE STATE</th><th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>TOTAL</th></tr>"

    tier1_total = int(np.sum([breakdown["Tier 1 Support"][p] for p in PRIORITY_SHORT]))
    tier2_total = int(np.sum([breakdown["Tier 2 Support"][p] for p in PRIORITY_SHORT]))

    row_tier1 = (
        f"<tr><td>Tier 1 Support</td>"
        f"<td>{build_link(breakdown['Tier 1 Support']['P1'], 'Tier 1 Support', 'P1-Critical')}</td>"
        f"<td>{build_link(breakdown['Tier 1 Support']['P2'], 'Tier 1 Support', 'P2-High')}</td>"
        f"<td>{build_link(breakdown['Tier 1 Support']['P3'], 'Tier 1 Support', 'P3-Medium')}</td>"
        f"<td>{build_link(breakdown['Tier 1 Support']['P4'], 'Tier 1 Support', 'P4-Low')}</td>"
        f"<td>{build_link(tier1_total, 'Tier 1 Support', None)}</td></tr>"
    )
    row_tier2 = (
        f"<tr><td>Tier 2 Support</td>"
        f"<td>{build_link(breakdown['Tier 2 Support']['P1'], 'Tier 2 Support', 'P1-Critical')}</td>"
        f"<td>{build_link(breakdown['Tier 2 Support']['P2'], 'Tier 2 Support', 'P2-High')}</td>"
        f"<td>{build_link(breakdown['Tier 2 Support']['P3'], 'Tier 2 Support', 'P3-Medium')}</td>"
        f"<td>{build_link(breakdown['Tier 2 Support']['P4'], 'Tier 2 Support', 'P4-Low')}</td>"
        f"<td>{build_link(tier2_total, 'Tier 2 Support', None)}</td></tr>"
    )
    row_grand = (
        f"<tr><td>Grand Total</td>"
        f"<td>{build_link(int(breakdown['Tier 1 Support']['P1'] + breakdown['Tier 2 Support']['P1']), None, 'P1-Critical')}</td>"
        f"<td>{build_link(int(breakdown['Tier 1 Support']['P2'] + breakdown['Tier 2 Support']['P2']), None, 'P2-High')}</td>"
        f"<td>{build_link(int(breakdown['Tier 1 Support']['P3'] + breakdown['Tier 2 Support']['P3']), None, 'P3-Medium')}</td>"
        f"<td>{build_link(int(breakdown['Tier 1 Support']['P4'] + breakdown['Tier 2 Support']['P4']), None, 'P4-Low')}</td>"
        f"<td>{build_link(grand_total, None, None)}</td></tr>"
    )

    st.markdown(
        f'<table class="assignment-table">{header}{row_tier1}{row_tier2}{row_grand}</table>',
        unsafe_allow_html=True,
    )
