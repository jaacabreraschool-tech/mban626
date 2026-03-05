import streamlit as st
import check_tickets
import submit_ticket
import ticket_counts

try:
    import tickets_assignment
except ModuleNotFoundError:
    tickets_assignment = None

# Page configuration
st.set_page_config(
    page_title="JAC-Global Ticketing System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stMainBlockContainer"] { background: #f5f5f5; padding: 2rem; }
    h1, h2, h3 { color: #1e3a5f; font-weight: 700; }
    [data-testid="metric-container"] {
        background: white; padding: 1.5rem; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

query_params = st.query_params
if query_params.get("view") == "assignment-details":
    if tickets_assignment is None:
        st.warning("Tickets Assignments module is missing.")
    else:
        tickets_assignment.show_details_page(
            assignee=query_params.get("assignee"),
            priority=query_params.get("priority"),
        )
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Submit Ticket",
    "📋 Tickets Assignments",
    "📊 Ticket Counts",
    "🔍 Check Tickets",
])

with tab1:
    submit_ticket.show()

with tab2:
    if tickets_assignment is None:
        st.warning(
            "Tickets Assignments module is missing. "
            "Create `tickets_assignment.py` to enable this section."
        )
    else:
        tickets_assignment.show()

with tab3:
    ticket_counts.show()

with tab4:
    check_tickets.show()
