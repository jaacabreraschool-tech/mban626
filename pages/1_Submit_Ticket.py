import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

st.set_page_config(page_title="JAC Global Ticketing", layout="wide")

# Apply theme
st.markdown("""
    <style>
    :root {
        --bg-shell: #f3f6fa;
        --bg-card: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #4b5563;
        --border-soft: #d1d9e6;
        --accent-primary: #0f3d66;
        --accent-secondary: #3b5f82;
        --accent-operational: #c98a2e;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: var(--bg-shell);
        padding: 2rem;
        color: var(--text-primary);
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    
    h1 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    
    h2, h3 {
        color: var(--text-secondary);
        font-weight: 700;
    }
    
    .stForm {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid var(--border-soft);
        box-shadow: 0 6px 14px rgba(18, 38, 58, 0.08);
    }
    
    .stButton > button {
        background: var(--accent-primary) !important;
        color: white !important;
        font-weight: 600 !important;
        border: 1px solid #0b2d4d !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 2px 6px rgba(15, 61, 102, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #0b2d4d !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(11, 45, 77, 0.24) !important;
    }
    
    [data-testid="metric-container"] {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--border-soft);
        box-shadow: 0 4px 10px rgba(31, 41, 55, 0.08);
        border-left: 5px solid var(--accent-operational);
    }

    [data-testid="stHorizontalBlock"] > div {
        gap: 0.8rem;
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary);
    }
    </style>
    """, unsafe_allow_html=True)

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


def show_center_popup(message):
    """Render a temporary centered popup message."""
    st.markdown(
        f"""
        <style>
        .ticket-popup {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #0f3d66;
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

def load_tickets():
    """Load tickets from CSV"""
    return pd.read_csv(TICKET_FILE) if os.path.exists(TICKET_FILE) else pd.DataFrame(columns=HEADERS)

def save_ticket(ticket_data):
    """Save a new ticket to CSV"""
    df = load_tickets()
    new_df = pd.concat([df, pd.DataFrame([ticket_data])], ignore_index=True)
    new_df.to_csv(TICKET_FILE, index=False)

def get_next_ticket_number(ticket_type):
    """Generate next ticket number based on type"""
    prefix_map = {
        "Problem": "PRB",
        "Incident": "INC",
        "Inquiry": "INQ"
    }
    prefix = prefix_map.get(ticket_type, "TKT")
    
    df = load_tickets()
    type_tickets = df[df["Type"] == ticket_type]
    next_number = len(type_tickets) + 1
    
    return f"{prefix}-{next_number:05d}"

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Submit Ticket", "Tickets Assignments", "📊 Ticket Counts"])

# TAB 1: Submit Ticket
with tab1:
    st.title("📋 JAC Global Ticketing System")
    st.markdown("### Create New Ticket")
    st.markdown("Fill in all fields below to submit a support ticket")
    st.markdown("---")

    # Create form columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Customer Name", placeholder="Enter full name")
        priority = st.selectbox(
            "Priority",
            ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"],
            placeholder="Select priority level"
        )
        product = st.selectbox(
            "Product Purchased",
            [
                "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign",
                "Microsoft Office 365", "Microsoft Teams", "Microsoft SharePoint",
                "Google Workspace", "Google Drive", "Google Meet",
                "Slack", "Asana", "Monday.com", "Trello", "Jira",
                "Salesforce CRM", "HubSpot", "Zoho CRM",
                "Mailchimp", "SendGrid", "Constant Contact",
                "Zendesk", "Freshdesk", "Intercom",
                "Figma", "Adobe XD", "InVision",
                "GitHub", "GitLab", "Bitbucket",
                "Docker", "Kubernetes", "Jenkins",
                "AWS S3", "Google Cloud Storage", "Azure Blob Storage",
                "Stripe", "PayPal", "Square",
                "Amazon Prime", "Netflix", "Disney+",
                "Spotify", "Apple Music", "YouTube Premium",
                "Sony PlayStation", "Microsoft Xbox"
            ],
            placeholder="Select product"
        )

    with col2:
        assigned_to = st.selectbox(
            "Assigned To",
            ["Tier 1 Support", "Tier 2 Support"],
            placeholder="Select support tier"
        )
        ticket_type = st.selectbox(
            "Type",
            ["Incident", "Problem", "Inquiry"],
            placeholder="Select ticket type"
        )
        date_of_purchase = st.date_input("Date of Purchase", value=datetime.now())

    st.markdown("---")

    short_desc = st.text_input("Short Description", placeholder="Brief issue summary")

    detailed_desc = st.text_area(
        "Detailed Description",
        placeholder="Provide detailed information about the issue...",
        height=130
    )

    st.markdown("---")

    # Submit button with validation
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🎫 Submit Ticket", use_container_width=True, type="primary"):
            # Validate all fields
            if not all([name, priority, assigned_to, product, date_of_purchase, ticket_type, short_desc, detailed_desc]):
                st.error("❌ Please fill in all required fields")
            else:
                # Generate ticket number
                ticket_number = get_next_ticket_number(ticket_type)
                
                # Create ticket data
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
                }
                
                # Save ticket
                save_ticket(ticket_data)
                
                # Success message
                show_center_popup(f"Ticket {ticket_number} submitted successfully")
                st.success(f"Ticket {ticket_number} submitted successfully")
                st.balloons()
                
                # Display ticket details
                st.markdown("### Ticket Confirmation")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Ticket Number**: {ticket_number}\n\n**Customer**: {name}\n\n**Priority**: {priority}")
                with col2:
                    st.info(f"**Type**: {ticket_type}\n\n**Assigned To**: {assigned_to}\n\n**Product**: {product}")

    with col2:
        if st.button("Clear Form", use_container_width=True):
            st.rerun()

# TAB 2: Tickets Assignments
with tab2:
    st.title("📋 Tickets Assignments")
    st.markdown("Overview of active tickets and key metrics")
    st.markdown("---")

    # Load data
    df = load_tickets()

    if len(df) == 0:
        st.warning("📭 No tickets yet. Submit your first ticket to see dashboard metrics.")
    else:
        # Display summary statistics
        st.markdown("## 📊 Key Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tickets", len(df), delta="Active")
        
        with col2:
            ticket_counts = np.array([len(df[df["Priority"] == p]) for p in ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]])
            avg_per_priority = np.mean(ticket_counts)
            st.metric("Avg per Priority", f"{avg_per_priority:.1f}")
        
        st.markdown("---")
        
        # Create visualizations
        st.markdown("## 📈 Ticket Analysis")
        
        # Priority Distribution Pie Chart
        st.markdown("### Tickets by Priority")
        
        # Count by priority using numpy
        priorities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
        counts = np.array([len(df[df["Priority"] == p]) for p in priorities])
        
        col_left, col_chart, col_right = st.columns([1, 2, 1])
        with col_chart:
            fig, ax = plt.subplots(figsize=(4, 4))
            colors = ['#0f3d66', '#3b5f82', '#6f8aa6', '#9aafc4']
            wedges, texts, autotexts = ax.pie(
                counts, labels=priorities, autopct='%1.1f%%',
                colors=colors, startangle=90, textprops={'fontsize': 7, 'fontweight': 'bold'}
            )
            
            # Make percentage text white
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(7)
            
            ax.set_title("Priority Distribution", fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)

        # Breakdown Table
        st.markdown("### Breakdown")
        
        tiers = ["Tier 1 Support", "Tier 2 Support"]
        priorities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
        
        breakdown_data = []
        for tier in tiers:
            tier_df = df[df["Assigned To"] == tier]
            row = {"ASSIGNEE STATE": tier}
            total = 0
            for p in priorities:
                count = len(tier_df[tier_df["Priority"] == p])
                row[p.split("-")[0]] = count
                total += count
            row["TOTAL"] = total
            breakdown_data.append(row)
        
        # Grand Total row
        grand = {"ASSIGNEE STATE": "Grand Total"}
        grand_total = 0
        for p in priorities:
            count = len(df[df["Priority"] == p])
            grand[p.split("-")[0]] = count
            grand_total += count
        grand["TOTAL"] = grand_total
        breakdown_data.append(grand)
        
        breakdown_df = pd.DataFrame(breakdown_data)
        
        st.markdown("""
        <style>
        .breakdown-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .breakdown-table th { background: #0f3d66; color: white; padding: 10px 16px; text-align: center; font-size: 13px; border-bottom: 3px solid #c98a2e; }
        .breakdown-table th:first-child { text-align: left; }
        .breakdown-table td { padding: 10px 16px; text-align: center; font-size: 13px; border-bottom: 1px solid #d1d9e6; background: #ffffff; color: #1f2937; }
        .breakdown-table td:first-child { text-align: left; font-style: italic; }
        .breakdown-table tr:last-child td { font-weight: bold; border-top: 2px solid #0f3d66; background: #eef3f8; }
        .breakdown-table td:last-child, .breakdown-table th:last-child { font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
        
        header = "<tr><th>ASSIGNEE STATE</th><th>P1</th><th>P2</th><th>P3</th><th>P4</th><th>TOTAL</th></tr>"
        rows = ""
        for _, r in pd.DataFrame(breakdown_data).iterrows():
            rows += f"<tr><td>{r['ASSIGNEE STATE']}</td><td>{r['P1']}</td><td>{r['P2']}</td><td>{r['P3']}</td><td>{r['P4']}</td><td>{r['TOTAL']}</td></tr>"
        
        st.markdown(f'<table class="breakdown-table">{header}{rows}</table>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("*Dashboard updates automatically when new tickets are submitted.*")

# TAB 3: Ticket Counts
with tab3:
    st.title("📊 Ticket Counts")
    st.markdown("Consolidated ticket totals and category breakdowns")
    st.markdown("---")

    df = load_tickets()

    if len(df) == 0:
        st.warning("📭 No tickets yet. Submit tickets to see counts.")
    else:
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

        left, right = st.columns(2)
        with left:
            st.markdown("### Count by Priority")
            priority_counts = (
                df["Priority"]
                .value_counts()
                .reindex(["P1-Critical", "P2-High", "P3-Medium", "P4-Low"], fill_value=0)
                .reset_index()
            )
            priority_counts.columns = ["Priority", "Count"]
            st.dataframe(priority_counts, hide_index=True, width="stretch")

        with right:
            st.markdown("### Count by Assignee")
            assignee_counts = df["Assigned To"].value_counts().reset_index()
            assignee_counts.columns = ["Assigned To", "Count"]
            st.dataframe(assignee_counts, hide_index=True, width="stretch")
