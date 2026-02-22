import streamlit as st
import pandas as pd
import io
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Product Sales Reporter",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def get_category(name):
    name_str = str(name).lower()
    
    def has_keyword(kw, s):
        return kw in s
    
    # Priority 1: Specific Categories
    specific_categories = [
        'Boxer', 'Jeans', 'Denim', 'Flannel', 'Polo', 
        'Panjabi', 'Trousers', 'Twill', 'Mask', 'Bag', 
        'Bottle', 'Contrast', 'Turtleneck', 'Wallet', 
        'Kaftan', 'Active Weare'
    ]
    
    for cat in specific_categories:
        if has_keyword(cat.lower(), name_str):
            return cat

    # Priority 2: FS/HS T-Shirt and Shirt logic
    is_full_sleeve = has_keyword('full sleeve', name_str)
    
    is_tshirt = has_keyword('t-shirt', name_str) or has_keyword('t shirt', name_str)
    if is_tshirt:
        return 'FS T-Shirt' if is_full_sleeve else 'HS T-Shirt'
        
    is_shirt = has_keyword('shirt', name_str)
    if is_shirt:
        return 'FS Shirt' if is_full_sleeve else 'HS Shirt'
        
    return 'Others'

def process_data(df):
    # Ensure necessary columns exist
    required_cols = ['Item Name', 'Item Cost', 'Quantity']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return None
            
    # Clean data
    df['Item Name'] = df['Item Name'].fillna('').astype(str)
    df['Item Cost'] = pd.to_numeric(df['Item Cost'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    
    # Categorize
    df['Category'] = df['Item Name'].apply(get_category)
    
    # Detailed Report
    report = df.groupby(['Category', 'Item Cost']).agg({
        'Quantity': 'sum'
    }).reset_index()
    
    report.columns = ['Category', 'Price (TK)', 'Total Quantity Sold']
    report['Total Amount (TK)'] = report['Price (TK)'] * report['Total Quantity Sold']
    report = report.sort_values(by=['Category', 'Price (TK)'])
    
    # Summary
    summary = report.groupby('Category').agg({
        'Total Quantity Sold': 'sum',
        'Total Amount (TK)': 'sum'
    }).reset_index()
    
    return report, summary

def main():
    st.title("📊 Smart Sales Report Generator")
    st.markdown("Upload your product list (Excel or CSV) to generate a categorized sales report with price-wise differentiation.")

    uploaded_file = st.file_uploader("Choose a file", type=['xlsx', 'csv'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success("File uploaded successfully!")
            
            if st.button("Generate Report"):
                report_df, summary_df = process_data(df)
                
                if report_df is not None:
                    # Metrics
                    total_qty = summary_df['Total Quantity Sold'].sum()
                    total_rev = summary_df['Total Amount (TK)'].sum()
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Total Quantity Sold", f"{total_qty:,.0f}")
                    col2.metric("Total Revenue", f"TK {total_rev:,.2f}")
                    
                    st.divider()
                    
                    # Display Summary
                    st.subheader("Summary by Category")
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # Display Detailed Report
                    st.subheader("Detailed Price-wise Report")
                    st.dataframe(report_df, use_container_width=True)
                    
                    # Download Section
                    st.divider()
                    st.subheader("📥 Download Report")
                    
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        report_df.to_excel(writer, sheet_name='Detailed Report', index=False)
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    st.download_button(
                        label="Download Excel Report",
                        data=buffer.getvalue(),
                        file_name="Sales_Report_Formatted.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
