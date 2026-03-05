import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Active Assignment", layout="wide")

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🏢 JAC-Global")
    st.markdown("---")
    st.markdown("### 📋 Pages")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📋 Submit Ticket", use_container_width=True):
            st.switch_page("pages/1_Submit_Ticket.py")
        if st.button("📋 Dashboard", use_container_width=True):
            st.switch_page("pages/2_Dashboard.py")

# Apply theme
st.markdown("""
    <style>
    [data-testid="stMainBlockContainer"] {
        background: #f5f5f5;
        padding: 2rem;
    }
    
    h1 {
        color: #1e3a5f;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #1e3a5f;
        font-weight: 700;
    }
    
    [data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }
    
    [data-testid="stDataFrameContainer"] {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

TICKET_FILE = "tickets.csv"
HEADERS = [
    "Ticket Number", "Name", "Priority", "Assigned To", "Product Purchased",
    "Date of Purchase", "Type", "Short Description", "Detailed Description",
]

def load_tickets():
    """Load tickets from CSV"""
    if os.path.exists(TICKET_FILE):
        df = pd.read_csv(TICKET_FILE)
        return df if len(df) > 0 else pd.DataFrame(columns=HEADERS)
    return pd.DataFrame(columns=HEADERS)

st.title("� Active Tickets Assignment Report")
st.markdown("Tier 1 vs Tier 2 Support Distribution by Priority")
st.markdown("---")

# Load data
df = load_tickets()

if len(df) == 0:
    st.warning("📭 No tickets yet. Submit tickets to see assignment reports.")
else:
    # Prepare priority data
    priorities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
    priority_short = ["P1", "P2", "P3", "P4"]
    
    # Initialize breakdown using numpy operations
    breakdown = {}
    for tier in ["Tier 1 Support", "Tier 2 Support"]:
        breakdown[tier] = {}
        for p_short, p_full in zip(priority_short, priorities):
            count = len(df[(df["Priority"] == p_full) & (df["Assigned To"] == tier)])
            breakdown[tier][p_short] = count
    
    # Calculate totals using numpy
    tier1_counts = np.array([breakdown["Tier 1 Support"][p] for p in priority_short])
    tier2_counts = np.array([breakdown["Tier 2 Support"][p] for p in priority_short])
    
    tier1_total = np.sum(tier1_counts)
    tier2_total = np.sum(tier2_counts)
    grand_total = tier1_total + tier2_total
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tier 1 Support", int(tier1_total), delta=f"{(tier1_total/grand_total*100):.1f}%")
    with col2:
        st.metric("Tier 2 Support", int(tier2_total), delta=f"{(tier2_total/grand_total*100):.1f}%")
    with col3:
        st.metric("Total Tickets", int(grand_total))
    
    st.markdown("---")
    
    # Create pie charts for each priority
    st.markdown("## Priority Distribution - Tier 1 vs Tier 2")
    
    col1, col2 = st.columns(2)
    
    for idx, (priority_short_val, priority_full) in enumerate(zip(priority_short, priorities)):
        if idx % 2 == 0:
            col = col1
        else:
            col = col2
        
        with col:
            st.markdown(f"### {priority_short_val}")
            
            tier1_val = breakdown["Tier 1 Support"][priority_short_val]
            tier2_val = breakdown["Tier 2 Support"][priority_short_val]
            total_val = tier1_val + tier2_val
            
            if total_val > 0:
                fig, ax = plt.subplots(figsize=(6, 5))
                
                sizes = [tier1_val, tier2_val]
                labels = ['Tier 1 Support', 'Tier 2 Support']
                colors = ['#667eea', '#dc3545']
                
                wedges, texts, autotexts = ax.pie(
                    sizes, labels=labels, autopct='%1.1f%%',
                    colors=colors, startangle=90,
                    textprops={'fontsize': 10, 'fontweight': 'bold'}
                )
                
                # Make percentage text white and bold
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                # Add count information below pie chart
                info_text = f"Tier 1: {int(tier1_val)} | Tier 2: {int(tier2_val)} | Total: {int(total_val)}"
                ax.text(0, -1.3, info_text, ha='center', fontsize=10, fontweight='bold')
                
                ax.set_title(f"{priority_short_val} Priority", fontsize=12, fontweight='bold', pad=20)
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info(f"No tickets with {priority_short_val} priority")
    
    st.markdown("---")
    
    # Breakdown table
    st.markdown("## Breakdown by Priority & Assignee")
    
    # Create breakdown dataframe
    breakdown_data = {
        "Assignee": ["Tier 1 Support", "Tier 2 Support", "Grand Total"],
        "P1": [
            breakdown["Tier 1 Support"]["P1"],
            breakdown["Tier 2 Support"]["P1"],
            breakdown["Tier 1 Support"]["P1"] + breakdown["Tier 2 Support"]["P1"]
        ],
        "P2": [
            breakdown["Tier 1 Support"]["P2"],
            breakdown["Tier 2 Support"]["P2"],
            breakdown["Tier 1 Support"]["P2"] + breakdown["Tier 2 Support"]["P2"]
        ],
        "P3": [
            breakdown["Tier 1 Support"]["P3"],
            breakdown["Tier 2 Support"]["P3"],
            breakdown["Tier 1 Support"]["P3"] + breakdown["Tier 2 Support"]["P3"]
        ],
        "P4": [
            breakdown["Tier 1 Support"]["P4"],
            breakdown["Tier 2 Support"]["P4"],
            breakdown["Tier 1 Support"]["P4"] + breakdown["Tier 2 Support"]["P4"]
        ],
        "TOTAL": [int(tier1_total), int(tier2_total), int(grand_total)]
    }
    
    df_breakdown = pd.DataFrame(breakdown_data)
    
    # Style the dataframe
    def style_breakdown(row):
        if row["Assignee"] == "Grand Total":
            return ['background-color: #667eea; color: white; font-weight: bold;'] * len(row)
        else:
            return [''] * len(row)
    
    styled_df = df_breakdown.style.apply(style_breakdown, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Additional statistics using numpy
    st.markdown("## Statistics Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Calculate proportion of Tier 1 vs Tier 2
        tier1_proportion = (tier1_total / grand_total * 100) if grand_total > 0 else 0
        st.metric("Tier 1 Load", f"{tier1_proportion:.1f}%")
    
    with col2:
        # Find highest priority workload
        p1_total = breakdown["Tier 1 Support"]["P1"] + breakdown["Tier 2 Support"]["P1"]
        p1_percent = (p1_total / grand_total * 100) if grand_total > 0 else 0
        st.metric("P1 Critical Load", f"{p1_percent:.1f}%")
    
    with col3:
        # Calculate average tickets per priority
        priority_averages = np.mean([
            breakdown["Tier 1 Support"]["P1"] + breakdown["Tier 2 Support"]["P1"],
            breakdown["Tier 1 Support"]["P2"] + breakdown["Tier 2 Support"]["P2"],
            breakdown["Tier 1 Support"]["P3"] + breakdown["Tier 2 Support"]["P3"],
            breakdown["Tier 1 Support"]["P4"] + breakdown["Tier 2 Support"]["P4"]
        ])
        st.metric("Avg per Priority", f"{priority_averages:.1f}")

st.markdown("---")
st.markdown("*Report updates automatically when new tickets are assigned.*")
