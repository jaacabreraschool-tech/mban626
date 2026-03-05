import streamlit as st
import pandas as pd
import os

TICKET_FILE = "tickets.csv"
HEADERS = [
    "Ticket Number", "Name", "Priority", "Assigned To",
    "Product Purchased", "Date of Purchase", "Type",
    "Short Description", "Detailed Description",
]

def load_tickets():
    return pd.read_csv(TICKET_FILE) if os.path.exists(TICKET_FILE) else pd.DataFrame(columns=HEADERS)

def show():
    st.title("🔍 Check Tickets")
    st.markdown("Search and review all ticket records")
    st.markdown("---")

    df = load_tickets()

    if len(df) == 0:
        st.warning("📭 No tickets yet.")
        return

    # Search filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_ticket = st.text_input("Search by Ticket Number", placeholder="e.g. INC-00001")
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "P1-Critical", "P2-High", "P3-Medium", "P4-Low"])
    with col3:
        filter_tier = st.selectbox("Filter by Assignee", ["All", "Tier 1 Support", "Tier 2 Support"])

    # Apply filters
    filtered = df.copy()
    if search_ticket:
        filtered = filtered[filtered["Ticket Number"].str.contains(search_ticket, case=False, na=False)]
    if filter_priority != "All":
        filtered = filtered[filtered["Priority"] == filter_priority]
    if filter_tier != "All":
        filtered = filtered[filtered["Assigned To"] == filter_tier]

    st.markdown(f"**Showing {len(filtered)} of {len(df)} tickets**")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
