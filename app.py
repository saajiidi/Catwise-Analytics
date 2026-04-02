import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import base64
from datetime import datetime
from io import BytesIO

# --- Configuration & Styling ---
FEEDBACK_DIR = "feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Modern Category Mapping
CATEGORY_MAPPING = {
    'Boxer': ['boxer'],
    'Tank Top': ['tank top', 'tanktop', 'tank', 'top'],
    'Jeans': ['jeans'],
    'Denim Shirt': ['denim'],
    'Flannel Shirt': ['flannel'],
    'Polo Shirt': ['polo'],
    'Panjabi': ['panjabi', 'punjabi'],
    'Trousers': ['trousers', 'pant', 'cargo', 'trouser', 'joggers', 'track pant', 'jogger'],
    'Twill Chino': ['twill chino'],
    'Mask': ['mask'],
    'Water Bottle': ['water bottle'],
    'Contrast Shirt': ['contrast'],
    'Turtleneck': ['turtleneck', 'mock neck'],
    'Drop Shoulder': ['drop', 'shoulder'],
    'Wallet': ['wallet'],
    'Kaftan Shirt': ['kaftan'],
    'Active Wear': ['active wear'],
    'Jersy': ['jersy'],
    'Sweatshirt': ['sweatshirt', 'hoodie', 'pullover'],
    'Jacket': ['jacket', 'outerwear', 'coat'],
    'Belt': ['belt'],
    'Sweater': ['sweater', 'cardigan', 'knitwear'],
    'Passport Holder': ['passport holder'],
    'Cap': ['cap'],
    'Leather Bag': ['bag', 'backpack'],
}

LOGO_PNG = "assets/deen_logo.png"

def load_logo():
    """Loads logo as base64 string from assets/deen_logo.png."""
    if os.path.exists(LOGO_PNG):
        try:
            with open(LOGO_PNG, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: pass
    return ""

def apply_custom_styles():
    """Applies premium CSS styles to the dashboard."""
    st.markdown("""
        <style>
        /* Base Container */
        .main { background-color: transparent; }
        
        /* Metric Styling - Premium Look */
        div[data-testid="stMetric"] { 
            background-color: var(--background-secondary, #ffffff); 
            padding: 24px; 
            border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 1px solid var(--secondary-background-color, #ececec);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            border-color: #007bff;
        }

        /* Metric Label Support */
        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin-bottom: 8px !important;
            color: var(--text-color, #1a1a1b) !important;
        }

        /* Metric Value - Ensure Full Visibility */
        [data-testid="stMetricValue"], 
        [data-testid="stMetricValue"] > div {
            font-weight: 800 !important;
            font-size: 1.5rem !important; /* Reduced for better fit on large numbers */
            color: var(--text-color, #1a1a1b) !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
            min-width: fit-content !important;
        }

        div[data-testid="stMetric"] {
            overflow: visible !important;
        }

        /* Dark Mode Text Consistency - Users specifically want white text */
        @media (prefers-color-scheme: dark) {
            [data-testid="stMetricLabel"], 
            [data-testid="stMetricValue"],
            [data-testid="stMetricValue"] > div { 
                color: #ffffff !important; 
            }
            div[data-testid="stMetric"] {
                background-color: #1e1e1e !important;
                border-color: #333 !important;
            }
        }

        /* Streamlit Dark Theme Detection */
        [data-theme="dark"] [data-testid="stMetricLabel"],
        [data-theme="dark"] [data-testid="stMetricValue"],
        [data-theme="dark"] [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
        }
        
        [data-theme="dark"] div[data-testid="stMetric"] {
            background-color: #1e1e1e !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            border: 1px solid #333;
        }

        .stButton>button { 
            width: 100%; 
            border-radius: 12px; 
            height: 3.5em; 
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); 
            color: white; 
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        div[data-testid="stExpander"] { 
            border: 1px solid var(--secondary-background-color, #eee); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            background: var(--background-secondary, white);
            border-radius: 14px;
            margin-bottom: 1.5rem;
            padding: 5px;
            transition: border-color 0.3s ease;
        }
        
        [data-theme="dark"] div[data-testid="stExpander"] {
            background-color: #1a1a1a !important;
            border-color: #333 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        @media (prefers-color-scheme: dark) {
            div[data-testid="stExpander"] {
                background-color: #1a1a1a !important;
                border-color: #333 !important;
            }
        }
        .sticky-footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #ffffff; /* Pure white in light mode */
            color: #000000 !important; /* Pure black in light mode */
            text-align: center;
            padding: 18px 0;
            border-top: 1px solid #e9ecef;
            z-index: 999;
            font-size: 0.9rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 -4px 30px rgba(0,0,0,0.06);
        }
        [data-theme="dark"] .sticky-footer {
            background-color: #121212 !important; /* Pure dark in dark mode */
            color: #ffffff !important;
            border-top: 1px solid #333 !important;
        }
        @media (prefers-color-scheme: dark) {
            .sticky-footer {
                background-color: #121212 !important;
                color: #ffffff !important;
            }
        }
        .footer-content-inner {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .brand-wrapper {
            display: flex;
            align-items: center;
            gap: 2px;
        }
        .small-logo {
            height: 24px;
            width: auto;
            filter: grayscale(0%);
        }
        .brand-name {
            font-weight: 600;
            color: #000000; /* Pure black in light mode */
        }
        [data-theme="dark"] .brand-name {
            color: #ffffff !important;
        }
        @media (prefers-color-scheme: dark) {
            .brand-name {
                color: #ffffff !important;
            }
        }
        .block-container {
            padding-bottom: 150px !important;
            padding-top: 3rem !important;
        }

        /* --- Theme-Aware Dynamic Styling --- */
        
        /* Universal Typography */
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
            color: var(--text-color) !important;
        }

        /* Metric Styling - Fully Dynamic */
        div[data-testid="stMetric"] { 
            background-color: var(--secondary-background-color); 
            padding: 24px; 
            border-radius: 16px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid rgba(128, 128, 128, 0.1);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-color: var(--primary-color);
        }

        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            opacity: 0.8;
            color: var(--text-color) !important;
        }

        [data-testid="stMetricValue"], 
        [data-testid="stMetricValue"] > div {
            font-weight: 800 !important;
            font-size: 1.6rem !important;
            color: var(--text-color) !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        /* UI Components - Inputs & Selectboxes */
        div[data-testid="stSelectbox"] > div, 
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextArea"] > div {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
        }

        /* Buttons - High Contrast Primary */
        .stButton>button { 
            width: 100%; 
            border-radius: 12px; 
            height: 3.5em; 
            background-color: var(--primary-color) !important;
            color: white !important; /* Buttons usually have white text regardless of theme */
            font-weight: 700;
            border: none;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            opacity: 0.9;
            transform: scale(1.01);
        }

        /* Tabs & Dividers */
        div[data-testid="stTabs"] button {
            color: var(--text-color) !important;
            opacity: 0.7;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--primary-color) !important;
            opacity: 1;
            border-bottom: 2px solid var(--primary-color) !important;
        }
        hr { border-color: rgba(128, 128, 128, 0.2) !important; }

        /* Expander & Notifications */
        div[data-testid="stExpander"], div[data-testid="stNotification"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid rgba(128, 128, 128, 0.1) !important;
            border-radius: 14px !important;
            color: var(--text-color) !important;
        }

        /* Sticky Footer - Dynamic Contrast & Always Fixed */
        .sticky-footer {
            position: fixed !important;
            left: 0 !important;
            bottom: 0 !important;
            right: 0 !important;
            width: 100% !important;
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
            text-align: center;
            padding: 20px 0;
            border-top: 1px solid rgba(128, 128, 128, 0.2);
            z-index: 999999;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 -5px 25px rgba(0,0,0,0.1);
        }
        
        [data-theme="dark"] .sticky-footer {
            background-color: #0e1117 !important; /* Pure black/dark for contrast */
            box-shadow: 0 -5px 25px rgba(0,0,0,0.4);
        }

        /* Force Whitish text specifically in Dark Mode */
        [data-theme="dark"] .sticky-footer, 
        [data-theme="dark"] .sticky-footer span,
        [data-theme="dark"] .brand-name {
            color: #f8f9fa !important;
        }
        
        @media (prefers-color-scheme: dark) {
            .sticky-footer, .brand-name {
                color: #f8f9fa !important;
            }
        }

        .brand-name {
            font-weight: 700;
            color: var(--primary-color);
        }

        /* --- Responsive Design --- */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-bottom: 220px !important;
            }
            .footer-content-inner {
                flex-direction: column;
                gap: 8px;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.3rem !important;
            }
            /* Keep footer fixed and prominent even on mobile */
            .sticky-footer {
                padding: 15px 5px !important;
            }
        }
        """, unsafe_allow_html=True)

# --- Helper Functions ---

def log_event(event_type, details):
    """Logs system events to JSON."""
    log_file = os.path.join(FEEDBACK_DIR, "system_logs.json")
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": event_type,
        "details": details
    }
    try:
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f: logs = json.load(f)
        logs.append(entry)
        with open(log_file, "w") as f: json.dump(logs[-100:], f, indent=4)
    except: pass

def get_product_category(name):
    """Categorizes product based on keywords."""
    name_str = str(name).lower()
    for cat, keywords in CATEGORY_MAPPING.items():
        if any(kw.lower() in name_str for kw in keywords):
            return cat
    
    # Special handling for T-Shirts and Shirts
    fs_keywords = ['full sleeve', 'long sleeve', 'fs', 'l/s']
    is_fs = any(kw in name_str for kw in fs_keywords)
    
    if any(kw in name_str for kw in ['t-shirt', 't shirt', 'tee']):
        return 'FS T-Shirt' if is_fs else 'T-Shirt'
    if 'shirt' in name_str:
        return 'FS Shirt' if is_fs else 'HS Shirt'
        
    return 'Others'

def find_columns(df):
    """Auto-detects columns from dataframe."""
    mapping = {
        'name': ['item name', 'product name', 'product', 'item', 'title', 'description', 'name'],
        'cost': ['item cost', 'price', 'unit price', 'cost', 'rate', 'mrp', 'selling price'],
        'qty': ['quantity', 'qty', 'units', 'sold', 'count', 'total quantity'],
        'date': ['date', 'order date', 'month', 'time', 'created at'],
        'order_id': ['order id', 'order #', 'invoice number', 'invoice #', 'order number', 'transaction id', 'id'],
        'phone': ['phone', 'contact', 'mobile', 'cell', 'phone number', 'customer phone']
    }
    found = {}
    actual_cols = list(df.columns)
    lower_cols = [c.strip().lower() for c in actual_cols]
    
    for key, aliases in mapping.items():
        # Exact match
        for alias in aliases:
            if alias in lower_cols:
                found[key] = actual_cols[lower_cols.index(alias)]
                break
        # Partial match
        if key not in found:
            for i, col in enumerate(lower_cols):
                if any(alias in col for alias in aliases):
                    found[key] = actual_cols[i]
                    break
    return found

def process_analytics(df, mapping):
    """Core data processing and metric calculation."""
    df = df.copy()
    
    # 1. Clean Data
    df['Clean_Name'] = df[mapping['name']].fillna('Unknown').astype(str)
    df = df[~df['Clean_Name'].str.contains('Choose Any', case=False, na=False)]
    df['Clean_Cost'] = pd.to_numeric(df[mapping['cost']], errors='coerce').fillna(0)
    df['Clean_Qty'] = pd.to_numeric(df[mapping['qty']], errors='coerce').fillna(0)
    df.loc[df['Clean_Qty'] < 0, 'Clean_Qty'] = 0
    df['Total Amount'] = df['Clean_Cost'] * df['Clean_Qty']
    df['Category'] = df['Clean_Name'].apply(get_product_category)
    
    # 2. Timeframe Detection
    timeframe = ""
    if mapping.get('date') and mapping['date'] in df.columns:
        try:
            dates = pd.to_datetime(df[mapping['date']], errors='coerce').dropna()
            if not dates.empty:
                if dates.dt.to_period('M').nunique() == 1:
                    timeframe = dates.iloc[0].strftime("%B_%Y")
                else:
                    timeframe = f"{dates.min().strftime('%d%b')}_to_{dates.max().strftime('%d%b_%y')}"
        except: timeframe = "Report"

    # 3. Aggregations
    summary = df.groupby('Category').agg({'Clean_Qty': 'sum', 'Total Amount': 'sum'}).reset_index()
    summary.columns = ['Category', 'Total Qty', 'Total Amount']
    
    t_rev = summary['Total Amount'].sum()
    t_qty = summary['Total Qty'].sum()
    if t_rev > 0: summary['Revenue Share (%)'] = (summary['Total Amount'] / t_rev * 100).round(2)
    if t_qty > 0: summary['Quantity Share (%)'] = (summary['Total Qty'] / t_qty * 100).round(2)
    
    drilldown = df.groupby(['Category', 'Clean_Cost']).agg({'Clean_Qty': 'sum', 'Total Amount': 'sum'}).reset_index()
    drilldown.columns = ['Category', 'Price (TK)', 'Total Qty', 'Total Amount']
    
    top_items = df.groupby('Clean_Name').agg({'Clean_Qty': 'sum', 'Total Amount': 'sum', 'Category': 'first'}).reset_index()
    top_items.columns = ['Product Name', 'Total Qty', 'Total Amount', 'Category']
    top_items = top_items.sort_values('Total Amount', ascending=False)
    
    # 4. Basket Metrics
    avg_basket_value = 0
    group_cols = [c for c in [mapping.get('order_id'), mapping.get('phone')] if c and c in df.columns]
    
    if group_cols:
        order_groups = df.groupby(group_cols).agg({'Total Amount': 'sum'})
        avg_basket_value = order_groups['Total Amount'].mean()
        
    return {
        'drilldown': drilldown,
        'summary': summary,
        'top_items': top_items,
        'timeframe': timeframe,
        'avg_basket_value': avg_basket_value,
        'total_qty': t_qty,
        'total_rev': t_rev,
        'total_orders': len(order_groups) if group_cols else 0
    }

# --- UI Components ---

def render_sidebar():
    with st.sidebar:
        st.header("💬 Feedback & Debug")
        comment = st.text_area("Report Issues:", placeholder="Category 'Polo' is incorrect...")
        if st.button("Submit Report"):
            feedback_file = os.path.join(FEEDBACK_DIR, "user_feedback.json")
            entry = {"timestamp": datetime.now().isoformat(), "comment": comment}
            try:
                data = []
                if os.path.exists(feedback_file):
                    with open(feedback_file, "r") as f: data = json.load(f)
                data.append(entry)
                with open(feedback_file, "w") as f: json.dump(data, f, indent=4)
                st.success("Feedback saved!")
            except: st.error("Failed to save.")
        
        st.divider()
        if st.checkbox("View System Logs"):
            log_path = os.path.join(FEEDBACK_DIR, "system_logs.json")
            if os.path.exists(log_path):
                with open(log_path, "r") as f: st.json(json.load(f)[-10:])
            else: st.info("No logs available.")

def render_footer(logo_b64):
    footer_html = f"""
    <div style="height: 120px;"></div> <!-- Spacer to prevent content overlap -->
    <div class="sticky-footer">
        <div class="footer-content-inner">
            <span>© {datetime.now().year} Sajid Islam. All rights reserved. | </span>
            <div class="brand-wrapper">
                <span style="opacity: 0.85;">Powered by</span>
                <img src="data:image/png;base64,{logo_b64}" class="small-logo">
                <span class="brand-name">DEEN Commerce</span>
            </div>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- Main App ---

def main():
    st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
    apply_custom_styles()
    
    logo_b64 = load_logo()
    render_sidebar()
    
    st.title("🚀 Sales Performance Dashboard")
    
    uploaded_file = st.file_uploader("Upload Sales Data (Excel or CSV)", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Attached: {uploaded_file.name}")
            
            # Column Mapping
            auto_cols = find_columns(df)
            all_cols = list(df.columns)
            mandatory_keys = ['name', 'cost', 'qty']
            is_mapped = all(k in auto_cols for k in mandatory_keys)
            
            if not is_mapped:
                st.subheader("🛠️ Verify Column Mapping")
                st.warning("⚠️ System couldn't auto-detect all mandatory columns. Please map them manually.")
                mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
                
                def get_idx(key):
                    return all_cols.index(auto_cols[key]) if key in auto_cols else 0

                m_name = mc1.selectbox("Product Name", all_cols, index=get_idx('name'))
                m_cost = mc2.selectbox("Price", all_cols, index=get_idx('cost'))
                m_qty = mc3.selectbox("Quantity", all_cols, index=get_idx('qty'))
                m_date = mc4.selectbox("Date (Opt)", ["None"] + all_cols, index=get_idx('date')+1 if 'date' in auto_cols else 0)
                m_order = mc5.selectbox("Order ID (Opt)", ["None"] + all_cols, index=get_idx('order_id')+1 if 'order_id' in auto_cols else 0)
                m_phone = mc6.selectbox("Phone (Opt)", ["None"] + all_cols, index=get_idx('phone')+1 if 'phone' in auto_cols else 0)
                
                mapping = {
                    'name': m_name, 'cost': m_cost, 'qty': m_qty,
                    'date': m_date if m_date != "None" else None,
                    'order_id': m_order if m_order != "None" else None,
                    'phone': m_phone if m_phone != "None" else None
                }
            else:
                mapping = {
                    'name': auto_cols['name'], 'cost': auto_cols['cost'], 'qty': auto_cols['qty'],
                    'date': auto_cols.get('date'),
                    'order_id': auto_cols.get('order_id'),
                    'phone': auto_cols.get('phone')
                }
                st.info(f"✨ **Auto-Mapped:** Name (**{mapping['name']}**), Price (**{mapping['cost']}**), Qty (**{mapping['qty']}**)")
            
            with st.expander("🔍 Preview Data"):
                preview_df = df.head(10).copy()
                preview_df.index = range(1, len(preview_df) + 1)
                st.dataframe(preview_df, use_container_width=True)

            if st.button("Generate Analytics"):
                results = process_analytics(df, mapping)
                
                # Metrics Row
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Orders", f"{results['total_orders']:,.0f}")
                m2.metric("Units Sold", f"{results['total_qty']:,.0f}")
                m3.metric("Gross Revenue", f"TK {results['total_rev']:,.2f}")
                
                # Show Basket Value if data available
                if results['avg_basket_value'] > 0:
                    m4.metric("Basket Size", f"TK {results['avg_basket_value']:,.2f}")
                else:
                    m4.metric("Basket Size", "0.00")

                st.divider()
                
                # Visuals
                v1, v2 = st.columns(2)
                
                # Sort once for consistent color sequence
                summ_sorted = results['summary'].sort_values('Total Amount', ascending=False)
                color_seq = px.colors.qualitative.Pastel
                
                v1.plotly_chart(px.pie(summ_sorted, values='Total Amount', names='Category', hole=0.5, 
                                       title='Revenue by Category', color_discrete_sequence=color_seq), use_container_width=True)
                
                v2.plotly_chart(px.bar(summ_sorted, x='Category', y='Total Qty', color='Category', 
                                       title='Volume by Category', color_discrete_sequence=color_seq), use_container_width=True)
                
                # Data Tables
                t1, t2, t3 = st.tabs(["📑 Breakdown", "🏆 Top Items", "🔍 Full List"])
                
                df_breakdown = results['summary'].sort_values('Total Amount', ascending=False).copy()
                df_breakdown.index = range(1, len(df_breakdown) + 1)
                
                df_top = results['top_items'].head(20).copy()
                df_top.index = range(1, len(df_top) + 1)
                
                df_drill = results['drilldown'].copy()
                df_drill.index = range(1, len(df_drill) + 1)

                with t1: st.dataframe(df_breakdown, use_container_width=True)
                with t2: st.dataframe(df_top, use_container_width=True)
                with t3: st.dataframe(df_drill, use_container_width=True)
                
                # Export
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                    results['summary'].to_excel(wr, sheet_name='Summary', index=False)
                    results['top_items'].to_excel(wr, sheet_name='Rankings', index=False)
                
                fname = f"Sales_Report_{results['timeframe']}.xlsx"
                st.download_button("📥 Download Report", data=buf.getvalue(), file_name=fname)
                
        except Exception as e:
            st.error(f"Processing Error: {e}")
            log_event("CRASH", str(e))

    render_footer(logo_b64)

if __name__ == "__main__":
    main()
