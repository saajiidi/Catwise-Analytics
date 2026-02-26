import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime
from io import BytesIO

# Configuration
FEEDBACK_DIR = "feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Set page configuration
st.set_page_config(
    page_title="Product Sales Reporter",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def log_system_event(event_type, details):
    """Logs errors or system events to a JSON file for further analysis."""
    log_file = os.path.join(FEEDBACK_DIR, "system_logs.json")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": timestamp,
        "type": event_type,
        "details": details
    }
    
    try:
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"Logging failed: {e}")

def save_user_feedback(comment):
    """Saves user comments to a feedback file."""
    feedback_file = os.path.join(FEEDBACK_DIR, "user_feedback.json")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    feedback_entry = {
        "timestamp": timestamp,
        "comment": comment
    }
    
    try:
        data = []
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                data = json.load(f)
        
        data.append(feedback_entry)
        with open(feedback_file, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

def get_category(name):
    """Categorizes products based on keywords in their names."""
    name_str = str(name).lower()
    
    def has_any(keywords, text):
        return any(kw.lower() in text for kw in keywords)
    
    specific_cats = {
        'Boxer': ['boxer'],
        'Jeans': ['jeans'],
        'Denim': ['denim'],
        'Flannel': ['flannel'],
        'Polo': ['polo'],
        'Panjabi': ['panjabi', 'punjabi'],
        'Trousers': ['trousers', 'pant', 'cargo', 'trouser', 'joggers', 'track pant', 'jogger'],
        'Twill Chino': ['twill chino'],
        'Mask': ['mask'],
        'Bag': ['bag', 'backpack'],
        'Water Bottle': ['water bottle'],
        'Contrast': ['contrast'],
        'Turtleneck': ['turtleneck', 'mock neck'],
        'Wallet': ['wallet'],
        'Kaftan': ['kaftan'],
        'Active Wear': ['active wear'],
        'Jersy': ['jersy'],
        'Sweatshirt': ['sweatshirt', 'hoodie', 'pullover'],
        'Jacket': ['jacket', 'outerwear', 'coat'],
        'Belt': ['belt'],
        'Sweater': ['sweater', 'cardigan', 'knitwear'],
        'Passport Holder': ['passport holder'],
        'Cap': ['cap'],
    }
    
    for cat, keywords in specific_cats.items():
        if has_any(keywords, name_str):
            return cat

    fs_keywords = ['full sleeve', 'long sleeve', 'fs', 'l/s']
    if has_any(['t-shirt', 't shirt', 'tee'], name_str):
        return 'FS T-Shirt' if has_any(fs_keywords, name_str) else 'HS T-Shirt'
        
    if has_any(['shirt'], name_str):
        return 'FS Shirt' if has_any(fs_keywords, name_str) else 'HS Shirt'
        
    return 'Others'

def find_columns(df):
    """Detects primary columns using exact and then partial matching."""
    mapping = {
        'name': ['item name', 'product name', 'product', 'item', 'title', 'description', 'name'],
        'cost': ['item cost', 'price', 'unit price', 'cost', 'rate', 'mrp', 'selling price'],
        'qty': ['quantity', 'qty', 'units', 'sold', 'count', 'total quantity'],
        'date': ['date', 'order date', 'month', 'time', 'created at']
    }
    
    found = {}
    actual_cols = [c.strip() for c in df.columns]
    lower_cols = [c.lower() for c in actual_cols]
    
    # 1. First Pass: Exact Matches (Case Insensitive)
    for key, aliases in mapping.items():
        for alias in aliases:
            if alias in lower_cols:
                idx = lower_cols.index(alias)
                found[key] = actual_cols[idx]
                break
    
    # 2. Second Pass: Partial Matches for missing keys
    for key, aliases in mapping.items():
        if key not in found:
            for col, l_col in zip(actual_cols, lower_cols):
                if any(alias in l_col for alias in aliases):
                    found[key] = col
                    break
                    
    return found

def process_data(df, selected_cols):
    """Processed data using validated user-selected or auto-detected columns."""
    try:
        df = df.copy()
        # Ensure 'Category' is calculated before grouping
        df['Internal_Name'] = df[selected_cols['name']].fillna('Unknown Product').astype(str)
        df['Internal_Cost'] = pd.to_numeric(df[selected_cols['cost']], errors='coerce').fillna(0)
        df['Internal_Qty'] = pd.to_numeric(df[selected_cols['qty']], errors='coerce').fillna(0)
        
        # Date processing for filename
        timeframe_suffix = ""
        if 'date' in selected_cols and selected_cols['date'] in df.columns:
            try:
                # Try to convert to datetime
                dates = pd.to_datetime(df[selected_cols['date']], errors='coerce').dropna()
                if not dates.empty:
                    # If all dates are in the same month, use Month Name, otherwise use Range
                    if dates.dt.to_period('M').nunique() == 1:
                        timeframe_suffix = dates.iloc[0].strftime("%B_%Y")
                    else:
                        timeframe_suffix = f"{dates.min().strftime('%d%b')}_to_{dates.max().strftime('%d%b_%y')}"
            except Exception:
                # If date parsing fails, just use the first non-null value as a fallback
                val = str(df[selected_cols['date']].dropna().iloc[0]) if not df[selected_cols['date']].dropna().empty else ""
                timeframe_suffix = val.replace("/", "-").replace(" ", "_")[:20]

        # Treatment for anomalies
        if (df['Internal_Qty'] < 0).any():
            log_system_event("DATA_ISSUE", "Found negative quantities, converted to 0.")
            df.loc[df['Internal_Qty'] < 0, 'Internal_Qty'] = 0

        df['Category'] = df['Internal_Name'].apply(get_category)
        df['Total Amount'] = df['Internal_Cost'] * df['Internal_Qty']
        
        # Track 'Others' for refinement
        others = df[df['Category'] == 'Others']
        if len(others) > 0:
            log_system_event("OTHERS_LOG", {"count": len(others), "samples": others['Internal_Name'].head(10).tolist()})

        # Analytics grouping
        summary = df.groupby('Category').agg({'Internal_Qty': 'sum', 'Total Amount': 'sum'}).reset_index()
        summary.columns = ['Category', 'Total Qty', 'Total Amount']
        
        total_rev = summary['Total Amount'].sum()
        total_qty = summary['Total Qty'].sum()
        if total_rev > 0: summary['Revenue Share (%)'] = (summary['Total Amount'] / total_rev * 100).round(2)
        if total_qty > 0: summary['Quantity Share (%)'] = (summary['Total Qty'] / total_qty * 100).round(2)
        
        drilldown = df.groupby(['Category', 'Internal_Cost']).agg({'Internal_Qty': 'sum', 'Total Amount': 'sum'}).reset_index()
        drilldown.columns = ['Category', 'Price (TK)', 'Total Qty', 'Total Amount']
        
        top_items = df.groupby('Internal_Name').agg({'Internal_Qty': 'sum', 'Total Amount': 'sum', 'Category': 'first'}).reset_index()
        top_items.columns = ['Product Name', 'Total Qty', 'Total Amount', 'Category']
        top_items = top_items.sort_values('Total Amount', ascending=False)
        
        return drilldown, summary, top_items, timeframe_suffix
    except Exception as e:
        log_system_event("CRASH", str(e))
        st.error(f"Error in calculation: {e}")
        return None, None, None, ""

def main():
    st.title("🚀 Sales Performance Dashboard")
    
    # Sidebar Feedback
    with st.sidebar:
        st.header("💬 Feedback & Logs")
        comment = st.text_area("Found an error? Report it here:", placeholder="e.g. 'Polo' items are misclassified...")
        if st.button("Submit Report"):
            if save_user_feedback(comment):
                st.success("Thank you! Feedback saved.")
            else:
                st.error("Submission failed.")
        
        st.divider()
        if st.checkbox("View Debug Logs"):
            log_path = os.path.join(FEEDBACK_DIR, "system_logs.json")
            if os.path.exists(log_path):
                with open(log_path, "r") as f: st.json(json.load(f)[-10:])
            else: st.write("No logs yet.")

    uploaded_file = st.file_uploader("Upload Sales Data (Excel or CSV)", type=['xlsx', 'csv'])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"File uploaded: {uploaded_file.name}")
            
            # Smart Column Mapping Selection
            auto_cols = find_columns(df)
            all_cols = list(df.columns)
            
            st.subheader("🛠️ Column Mapping")
            st.info("We've detected your columns. Please verify or correct them before generating the report.")
            
            c_sel1, c_sel2, c_sel3, c_sel4 = st.columns(4)
            
            def get_col_idx(key):
                if key in auto_cols and auto_cols[key] in all_cols:
                    return all_cols.index(auto_cols[key])
                return 0

            mapped_name = c_sel1.selectbox("Product Name", all_cols, index=get_col_idx('name'))
            mapped_cost = c_sel2.selectbox("Price/Cost", all_cols, index=get_col_idx('cost'))
            mapped_qty = c_sel3.selectbox("Quantity", all_cols, index=get_col_idx('qty'))
            mapped_date = c_sel4.selectbox("Date (Optional)", ["None"] + all_cols, index=get_col_idx('date') + 1 if 'date' in auto_cols else 0)
            
            final_mapping = {
                'name': mapped_name, 
                'cost': mapped_cost, 
                'qty': mapped_qty,
                'date': mapped_date if mapped_date != "None" else None
            }
            
            with st.expander("🔍 Search Raw Data"):
                search = st.text_input("Product search...")
                if search: st.dataframe(df[df[mapped_name].str.contains(search, case=False, na=False)], use_container_width=True)
                else: st.dataframe(df.head(10), use_container_width=True)

            if st.button("Generate Dashboard"):
                drill, summ, top, timeframe = process_data(df, final_mapping)
                if drill is not None:
                    t_qty, t_rev = summ['Total Qty'].sum(), summ['Total Amount'].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Sold", f"{t_qty:,.0f}")
                    c2.metric("Revenue", f"TK {t_rev:,.2f}")
                    c3.metric("Avg Price", f"TK {(t_rev/t_qty if t_qty > 0 else 0):,.2f}")
                    
                    st.divider()
                    v1, v2 = st.columns(2)
                    v1.plotly_chart(px.pie(summ, values='Total Amount', names='Category', hole=0.5, title='Revenue Share', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
                    v2.plotly_chart(px.bar(summ.sort_values('Total Qty', ascending=False), x='Category', y='Total Qty', color='Category', title='Volume by Category', color_discrete_sequence=px.colors.qualitative.Bold), use_container_width=True)
                    
                    tabs = st.tabs(["📑 Summary", "🏆 Rankings", "🔍 Drilldown"])
                    with tabs[0]: st.dataframe(summ.sort_values('Total Amount', ascending=False), use_container_width=True, hide_index=True)
                    with tabs[1]: st.dataframe(top.head(20), use_container_width=True, hide_index=True)
                    with tabs[2]: st.dataframe(drill.sort_values(['Category', 'Price (TK)']), use_container_width=True, hide_index=True)
                    
                    buf = BytesIO()
                    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                        summ.to_excel(wr, sheet_name='Summary', index=False)
                        top.to_excel(wr, sheet_name='Rankings', index=False)
                        drill.to_excel(wr, sheet_name='Details', index=False)
                    
                    # Generate dynamic filename
                    base_name = uploaded_file.name.split('.')[0]
                    file_suffix = f"_{timeframe}" if timeframe else ""
                    final_filename = f"Report_{base_name}{file_suffix}.xlsx"
                    
                    st.download_button("📥 Export Report", data=buf.getvalue(), file_name=final_filename)
                    
        except Exception as e:
            log_system_event("FILE_ERROR", str(e))
            st.error(f"File error: {e}")

if __name__ == "__main__":
    main()
