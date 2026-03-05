import os
from datetime import date

import matplotlib.pyplot as plt
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


def load_tickets() -> pd.DataFrame:
    if os.path.exists(TICKET_FILE):
        return pd.read_csv(TICKET_FILE)
    return pd.DataFrame(columns=HEADERS)


def show() -> None:
    st.title("Ticket Counts")
    st.markdown("Consolidated ticket totals and category breakdowns")
    st.markdown("---")

    df = load_tickets()

    if len(df) == 0:
        st.warning("No tickets yet. Submit tickets to see counts.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(df))
    with col2:
        st.metric("Incidents", int((df["Type"] == "Incident").sum()))
    with col3:
        st.metric("Problems", int((df["Type"] == "Problem").sum()))
    with col4:
        st.metric("Inquiries", int((df["Type"] == "Inquiry").sum()))

    st.markdown("---")

    dated_df = df.copy()
    # Use Submitted At if available, fall back to Date of Purchase for old tickets
    dated_df["Submitted At"] = pd.to_datetime(dated_df.get("Submitted At"), errors="coerce")
    dated_df["Date of Purchase"] = pd.to_datetime(dated_df["Date of Purchase"], format="mixed", errors="coerce")
    dated_df["Timestamp"] = dated_df["Submitted At"].fillna(dated_df["Date of Purchase"])
    dated_df = dated_df.dropna(subset=["Timestamp"])

    st.markdown("### Trends")
    tab_hourly, tab_daily, tab_weekly, tab_monthly, tab_quarterly, tab_yearly = st.tabs([
        "Hourly",
        "Daily",
        "Weekly",
        "Monthly",
        "Quarterly",
        "Yearly",
    ])

    if len(dated_df) == 0:
        st.info("No valid dates available for trend tabs.")
        return

    dated_df["Open Date"] = dated_df["Timestamp"].dt.floor("D")
    today = pd.Timestamp(date.today())
    dated_df["Backlog Days"] = (today - dated_df["Open Date"]).dt.days.clip(lower=0)

    priority_order = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
    priority_short = ["P1", "P2", "P3", "P4"]

    st.markdown(
        """
        <style>
        .tc-box-title {
            background: #0c4da2;
            color: #ffffff;
            font-weight: 700;
            padding: 8px 10px;
            border: 1px solid #083977;
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            font-size: 14px;
        }
        .tc-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #cfd7e4;
            font-size: 13px;
            margin-bottom: 12px;
        }
        .tc-table th, .tc-table td {
            border: 1px solid #d9e1ec;
            padding: 8px;
            text-align: center;
        }
        .tc-table th:first-child, .tc-table td:first-child {
            text-align: left;
        }
        .tc-head-main {
            background: #f3f6fb;
            color: #2f3f55;
            font-weight: 700;
        }
        .tc-p1 { background: #e67e22; color: #1f1f1f; font-weight: 700; }
        .tc-p2 { background: #f4d03f; color: #1f1f1f; font-weight: 700; }
        .tc-p3 { background: #6ab04c; color: #1f1f1f; font-weight: 700; }
        .tc-p4 { background: #2e86de; color: #ffffff; font-weight: 700; }
        .tc-avg { background: #23395b; color: #ffffff; font-weight: 700; }
        .tc-grand { background: #f1f4f8; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    def build_breakdown_table(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
        pivot = frame.pivot_table(
            index=group_col,
            columns="Priority",
            values="Ticket Number",
            aggfunc="count",
            fill_value=0,
            observed=False,
        )
        pivot = pivot.reindex(columns=priority_order, fill_value=0)
        pivot.columns = priority_short
        pivot = pivot.reset_index().rename(columns={group_col: "Created"})
        total_row = {
            "Created": "Grand Total",
            "P1": int(pivot["P1"].sum()) if len(pivot) else 0,
            "P2": int(pivot["P2"].sum()) if len(pivot) else 0,
            "P3": int(pivot["P3"].sum()) if len(pivot) else 0,
            "P4": int(pivot["P4"].sum()) if len(pivot) else 0,
        }
        return pd.concat([pivot, pd.DataFrame([total_row])], ignore_index=True)

    def build_avg_table(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
        group_count = max(frame[group_col].nunique(), 1)
        avg_row = {"Metric": "Priority Average"}
        count_row = {"Metric": "Ticket Count"}

        for p_short, p_full in zip(priority_short, priority_order):
            subset = frame[frame["Priority"] == p_full]
            avg_row[p_short] = round(float(len(subset) / group_count), 2) if len(subset) else 0
            count_row[p_short] = int(len(subset))

        avg_row["AVG"] = round(float(len(frame) / group_count), 2) if len(frame) else 0
        count_row["AVG"] = int(len(frame))
        return pd.DataFrame([avg_row, count_row])

    def render_breakdown_html(frame: pd.DataFrame, group_col: str, title_suffix: str) -> None:
        breakdown_df = build_breakdown_table(frame, group_col)
        header_label = f"TICKET COUNT<br>{title_suffix.upper()}"

        rows_html = ""
        for _, row in breakdown_df.iterrows():
            row_class = "tc-grand" if str(row["Created"]) == "Grand Total" else ""
            rows_html += (
                f"<tr class='{row_class}'>"
                f"<td>{row['Created']}</td>"
                f"<td>{int(row['P1'])}</td>"
                f"<td>{int(row['P2'])}</td>"
                f"<td>{int(row['P3'])}</td>"
                f"<td>{int(row['P4'])}</td>"
                "</tr>"
            )

        table_html = (
            "<div class='tc-box-title'>Breakdown [" + title_suffix + "]</div>"
            "<table class='tc-table'>"
            f"<tr><th class='tc-head-main'>{header_label}</th>"
            "<th class='tc-p1'>P1</th><th class='tc-p2'>P2</th><th class='tc-p3'>P3</th><th class='tc-p4'>P4</th></tr>"
            + rows_html
            + "</table>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    def render_avg_html(frame: pd.DataFrame, group_col: str) -> None:
        avg_df = build_avg_table(frame, group_col)
        rows_html = ""
        for _, row in avg_df.iterrows():
            is_count = row["Metric"] == "Ticket Count"
            fmt = lambda v: str(int(v)) if is_count else str(v)
            rows_html += (
                "<tr>"
                f"<td><b>{row['Metric']}</b></td>"
                f"<td>{fmt(row['P1'])}</td><td>{fmt(row['P2'])}</td><td>{fmt(row['P3'])}</td><td>{fmt(row['P4'])}</td><td><b>{fmt(row['AVG'])}</b></td>"
                "</tr>"
            )

        table_html = (
            "<table class='tc-table'>"
            "<tr><th class='tc-head-main'>AVERAGE BACKLOG</th>"
            "<th class='tc-p1'>P1</th><th class='tc-p2'>P2</th><th class='tc-p3'>P3</th><th class='tc-p4'>P4</th><th class='tc-avg'>AVG</th></tr>"
            + rows_html
            + "</table>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    def render_layout(frame: pd.DataFrame, group_col: str, title_suffix: str) -> None:
        left, right = st.columns([1.05, 1.95], gap="medium")

        with left:
            render_breakdown_html(frame, group_col, title_suffix)
            render_avg_html(frame, group_col)

        with right:
            st.markdown("#### Ticket Count Trend")
            pivot = pd.crosstab(frame[group_col], frame["Priority"])
            pivot = pivot.reindex(columns=priority_order, fill_value=0)
            if hasattr(frame[group_col], "cat"):
                pivot = pivot.reindex(frame[group_col].cat.categories, fill_value=0)
            else:
                pivot = pivot.sort_index()

            if len(pivot) == 0:
                st.info("No data available for selected period.")
                return

            x = range(len(pivot.index))
            p1 = pivot["P1-Critical"].values
            p2 = pivot["P2-High"].values
            p3 = pivot["P3-Medium"].values
            p4 = pivot["P4-Low"].values
            avg_line = (p1 + p2 + p3 + p4) / 4

            fig, ax = plt.subplots(figsize=(8.4, 4.6))
            ax.bar(x, p1, label="P1", color="#d35400")
            ax.bar(x, p2, bottom=p1, label="P2", color="#f1c40f")
            ax.bar(x, p3, bottom=p1 + p2, label="P3", color="#2e7d32")
            ax.bar(x, p4, bottom=p1 + p2 + p3, label="P4", color="#1e88e5")
            ax.plot(x, avg_line, color="#2f2f2f", linestyle="--", marker="o", linewidth=2, label="Priority Average")

            ax.set_xticks(list(x))
            labels = [str(v) for v in pivot.index]
            rotation = 45 if title_suffix == "Hourly" else 0
            ax.set_xticklabels(labels, rotation=rotation, fontsize=8, ha="right" if rotation else "center")
            ax.set_ylabel("Ticket Count")
            ax.set_xlabel(title_suffix)
            ax.grid(axis="y", alpha=0.25)
            ax.legend(loc="upper right", frameon=False)
            st.pyplot(fig)

    def apply_selector(tab_key: str, label: str, options: list[str], default_index: int = 0) -> str:
        sel_col, _ = st.columns([1, 5])
        with sel_col:
            selected = st.selectbox(label, options, index=default_index, key=f"{tab_key}_candidate")
        return selected

    def apply_date_selector(
        tab_key: str,
        label: str,
        min_value: date,
        max_value: date,
        default_value: date,
    ) -> date:
        sel_col, _ = st.columns([1, 5])
        with sel_col:
            selected = st.date_input(
                label,
                value=default_value,
                min_value=min_value,
                max_value=max_value,
                key=f"{tab_key}_candidate",
            )
        return selected

    with tab_hourly:
        min_date = dated_df["Open Date"].min().date()
        max_date = dated_df["Open Date"].max().date()
        today_date = date.today()
        default_date = today_date if min_date <= today_date <= max_date else max_date
        selected_date = apply_date_selector("hourly", "Select Date", min_date, max_date, default_date)
        filtered = dated_df[dated_df["Open Date"].dt.date == selected_date].copy()
        filtered["Hour"] = filtered["Timestamp"].dt.strftime("%I:00 %p").str.lstrip("0")
        all_hours = [pd.Timestamp(f"2000-01-01 {h:02d}:00").strftime("%I:00 %p").lstrip("0") for h in range(24)]
        filtered["Hour"] = pd.Categorical(filtered["Hour"], categories=all_hours, ordered=True)
        render_layout(filtered, "Hour", "Hourly")

    with tab_daily:
        dated_df["Week Start"] = dated_df["Open Date"] - pd.to_timedelta(dated_df["Open Date"].dt.weekday, unit="D")
        week_starts = sorted(dated_df["Week Start"].dropna().unique().tolist(), reverse=True)
        week_map = {
            pd.Timestamp(w).strftime("Week %V (%b %-d, %Y)"): pd.Timestamp(w)
            for w in week_starts
        }
        week_labels = list(week_map.keys())
        # Default to the week containing today
        today_ws = pd.Timestamp(date.today()) - pd.to_timedelta(pd.Timestamp(date.today()).weekday(), unit="D")
        default_idx = next((i for i, w in enumerate(week_starts) if pd.Timestamp(w) == today_ws), 0)
        default_week = week_labels[default_idx]
        selected_week_label = apply_selector("daily", "Select Week", week_labels, default_index=default_idx)
        selected_week_start = week_map[selected_week_label]
        filtered = dated_df[dated_df["Week Start"] == selected_week_start].copy()
        filtered["Open Date Label"] = filtered["Open Date"].dt.strftime("%Y-%m-%d")
        render_layout(filtered, "Open Date Label", "Daily")

    with tab_weekly:
        dated_df["Month Label"] = dated_df["Open Date"].dt.to_period("M").astype(str)
        month_options = sorted(dated_df["Month Label"].unique().tolist(), reverse=True)
        current_month = pd.Timestamp(date.today()).to_period("M").strftime("%Y-%m")
        month_idx = next((i for i, m in enumerate(month_options) if m == current_month), 0)
        selected_month = apply_selector("weekly", "Select Month", month_options, default_index=month_idx)
        filtered = dated_df[dated_df["Month Label"] == selected_month].copy()
        filtered["Week Label"] = filtered["Open Date"].dt.to_period("W").astype(str)
        render_layout(filtered, "Week Label", "Weekly")

    with tab_monthly:
        dated_df["Year Label"] = dated_df["Open Date"].dt.year.astype(str)
        year_options = sorted(dated_df["Year Label"].unique().tolist(), reverse=True)
        current_year = str(date.today().year)
        year_idx = next((i for i, y in enumerate(year_options) if y == current_year), 0)
        selected_year = apply_selector("monthly", "Select Year", year_options, default_index=year_idx)
        filtered = dated_df[dated_df["Year Label"] == selected_year].copy()
        filtered["Month Label"] = filtered["Open Date"].dt.to_period("M").astype(str)
        render_layout(filtered, "Month Label", "Monthly")

    with tab_quarterly:
        year_options = sorted(dated_df["Open Date"].dt.year.astype(str).unique().tolist(), reverse=True)
        current_year = str(date.today().year)
        year_idx = next((i for i, y in enumerate(year_options) if y == current_year), 0)
        selected_year = apply_selector("quarterly", "Select Year", year_options, default_index=year_idx)
        filtered = dated_df[dated_df["Open Date"].dt.year.astype(str) == selected_year].copy()
        filtered["Quarter Label"] = "Q" + filtered["Open Date"].dt.quarter.astype(str)
        render_layout(filtered, "Quarter Label", "Quarterly")

    with tab_yearly:
        filtered = dated_df.copy()
        filtered["Year Label"] = filtered["Open Date"].dt.year.astype(str)
        render_layout(filtered, "Year Label", "Yearly")
