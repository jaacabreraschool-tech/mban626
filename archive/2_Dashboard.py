import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Dashboard", layout="wide")

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
            st.rerun()

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

st.title("� Dashboard")
st.markdown("Overview of active tickets and key metrics")
st.markdown("---")

# Load data
df = load_tickets()

if len(df) == 0:
    st.warning("📭 No tickets yet. Submit your first ticket to see dashboard metrics.")
else:
    # Display summary statistics
    st.markdown("## Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", len(df), delta="Active")
    
    with col2:
        p1_count = len(df[df["Priority"] == "P1-Critical"])
        st.metric("Critical (P1)", p1_count)
    
    with col3:
        tier1_count = len(df[df["Assigned To"] == "Tier 1 Support"])
        st.metric("Tier 1 Support", tier1_count)
    
    with col4:
        avg_products = len(df["Product Purchased"].unique())
        st.metric("Unique Products", avg_products)
    
    st.markdown("---")
    
    # Create visualizations
    st.markdown("## Ticket Analysis")
    
    # 1. Priority Distribution using Matplotlib
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Tickets by Priority")
        
        # Count by priority using numpy
        priorities = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
        counts = np.array([len(df[df["Priority"] == p]) for p in priorities])
        
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#dc3545', '#fd7e14', '#0dcaf0', '#198754']
        bars = ax.bar(range(len(priorities)), counts, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xticks(range(len(priorities)))
        ax.set_xticklabels([p.split('-')[0] for p in priorities])
        ax.set_ylabel("Count", fontsize=11, fontweight='bold')
        ax.set_title("Tickets by Priority Level", fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # 2. Type Distribution using Matplotlib
    with col2:
        st.markdown("### Tickets by Type")
        
        types = df["Type"].unique()
        type_counts = np.array([len(df[df["Type"] == t]) for t in types])
        
        fig, ax = plt.subplots(figsize=(8, 5))
        colors_type = ['#667eea', '#764ba2', '#f093fb']
        wedges, texts, autotexts = ax.pie(
            type_counts, labels=types, autopct='%1.1f%%',
            colors=colors_type, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        
        # Make percentage text white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title("Tickets by Type", fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # 3. Assignment Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Support Tier Distribution")
        
        assignment_data = df["Assigned To"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        
        colors_assign = ['#667eea', '#dc3545']
        bars = ax.barh(assignment_data.index, assignment_data.values, color=colors_assign, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / assignment_data.sum()) * 100
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)} ({percentage:.1f}%)',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlabel("Count", fontsize=11, fontweight='bold')
        ax.set_title("Distribution by Support Tier", fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # 4. Top 10 Products
    with col2:
        st.markdown("### Top 10 Products")
        
        product_counts = df["Product Purchased"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        
        colors_prod = plt.cm.Set3(np.linspace(0, 1, len(product_counts)))
        bars = ax.barh(range(len(product_counts)), product_counts.values, color=colors_prod, edgecolor='black', linewidth=1.5)
        
        ax.set_yticks(range(len(product_counts)))
        ax.set_yticklabels(product_counts.index, fontsize=9)
        ax.set_xlabel("Count", fontsize=11, fontweight='bold')
        ax.set_title("Most Popular Products", fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, product_counts.values)):
            ax.text(val, bar.get_y() + bar.get_height()/2.,
                   f'{int(val)}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Calculation Statistics using numpy
    st.markdown("## Statistical Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticket_counts = np.array([len(df[df["Priority"] == p]) for p in ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]])
        avg_per_priority = np.mean(ticket_counts)
        st.metric("Avg Tickets per Priority", f"{avg_per_priority:.1f}")
    
    with col2:
        tier_counts = df["Assigned To"].value_counts()
        if len(tier_counts) > 0:
            avg_per_tier = np.mean(tier_counts.values)
            st.metric("Avg Tickets per Tier", f"{avg_per_tier:.1f}")
    
    with col3:
        unique_products = len(df["Product Purchased"].unique())
        total_tickets = len(df)
        products_ratio = unique_products / total_tickets if total_tickets > 0 else 0
        st.metric("Product Variety", f"{products_ratio:.2%}")

st.markdown("---")
st.markdown("*Dashboard updates automatically when new tickets are submitted.*")
