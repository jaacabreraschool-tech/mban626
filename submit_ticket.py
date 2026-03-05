import os
from datetime import datetime

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
    "Submitted At",
]


def show_center_popup(message: str) -> None:
    """Render a temporary centered popup message."""
    st.markdown(
        f"""
        <style>
        .ticket-popup {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #198754;
            color: #ffffff;
            padding: 14px 22px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
            z-index: 99999;
            animation: popupFade 2.6s ease forwards;
            pointer-events: none;
        }}

        @keyframes popupFade {{
            0% {{ opacity: 0; }}
            12% {{ opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        </style>
        <div class="ticket-popup">{message}</div>
        """,
        unsafe_allow_html=True,
    )


def load_tickets() -> pd.DataFrame:
    if os.path.exists(TICKET_FILE):
        return pd.read_csv(TICKET_FILE)
    return pd.DataFrame(columns=HEADERS)


def save_ticket(ticket_data: dict) -> None:
    df = load_tickets()
    new_df = pd.concat([df, pd.DataFrame([ticket_data])], ignore_index=True)
    new_df.to_csv(TICKET_FILE, index=False)


def get_next_ticket_number(ticket_type: str) -> str:
    prefix_map = {"Problem": "PRB", "Incident": "INC", "Inquiry": "INQ"}
    prefix = prefix_map.get(ticket_type, "TKT")

    df = load_tickets()
    next_number = len(df[df["Type"] == ticket_type]) + 1
    return f"{prefix}-{next_number:05d}"


def show() -> None:
    if st.session_state.get("clear_submit_form_requested", False):
        # Reset widget-bound keys before creating widgets in this run.
        st.session_state["submit_name"] = ""
        st.session_state["submit_priority"] = "P1-Critical"
        st.session_state["submit_product"] = "Adobe Photoshop"
        st.session_state["submit_assigned_to"] = "Tier 1 Support"
        st.session_state["submit_type"] = "Incident"
        st.session_state["submit_date"] = datetime.now().date()
        st.session_state["submit_short_desc"] = ""
        st.session_state["submit_detailed_desc"] = ""
        st.session_state["clear_submit_form_requested"] = False

    if "submit_date" not in st.session_state:
        st.session_state["submit_date"] = datetime.now().date()

    st.title("Create a new support ticket")
    st.markdown("")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Customer Name", placeholder="Enter full name", key="submit_name")
        priority = st.selectbox(
            "Priority",
            ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"],
            key="submit_priority",
        )
        product = st.selectbox(
            "Product Purchased",
            [
                "Adobe Photoshop",
                "Microsoft Office 365",
                "Google Workspace",
                "Slack",
                "Salesforce CRM",
                "Zendesk",
                "GitHub",
                "AWS S3",
                "Stripe",
                "Sony PlayStation",
                "Microsoft Xbox",
            ],
            key="submit_product",
        )

    with col2:
        assigned_to = st.selectbox(
            "Assigned To",
            ["Tier 1 Support", "Tier 2 Support"],
            key="submit_assigned_to",
        )
        ticket_type = st.selectbox(
            "Type",
            ["Incident", "Problem", "Inquiry"],
            key="submit_type",
        )
        date_of_purchase = st.date_input("Date of Purchase", max_value=datetime.now().date(), key="submit_date")

    short_desc = st.text_input(
        "Short Description", placeholder="Brief issue summary", key="submit_short_desc"
    )
    detailed_desc = st.text_area(
        "Detailed Description",
        placeholder="Provide detailed information about the issue...",
        height=130,
        key="submit_detailed_desc",
    )

    all_filled = all([name.strip(), short_desc.strip(), detailed_desc.strip()])

    submit_col, clear_col = st.columns([2, 1])

    with submit_col:
        if st.button("Submit Ticket", type="primary", width="stretch", key="submit_btn", disabled=not all_filled):

            ticket_number = get_next_ticket_number(ticket_type)
            ticket_data = {
                "Ticket Number": ticket_number,
                "Name": name,
                "Priority": priority,
                "Assigned To": assigned_to,
                "Product Purchased": product,
                "Date of Purchase": date_of_purchase,
                "Type": ticket_type,
                "Short Description": short_desc,
                "Detailed Description": detailed_desc,
                "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_ticket(ticket_data)

            show_center_popup(f"Ticket {ticket_number} submitted successfully")

    with clear_col:
        if st.button("Clear Form", width="stretch", key="clear_btn"):
            st.session_state["clear_submit_form_requested"] = True
            st.rerun()
