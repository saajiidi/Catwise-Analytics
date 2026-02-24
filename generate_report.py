import pandas as pd
import os

def generate_report(file_path):
    df = pd.read_excel(file_path)
    
    # Pre-process columns
    df['Item Name'] = df['Item Name'].fillna('').astype(str)
    df['Item Cost'] = pd.to_numeric(df['Item Cost'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    
    def get_category(name):
        name_str = name.lower()
        
        # Helper for keywords
        def has_keyword(kw, s):
            return kw in s
        
        # Priority 1: Specific Categories from the list
        # We check these first because a "Polo Shirt" should be "Polo"
        # and a "Flannel Shirt" should be "Flannel".
        specific_categories = [
            'Boxer', 'Jeans', 'Flannel', 'Denim', 'Polo', 
            'Panjabi', 'Trousers', 'Twill', 'Mask', 'Bag', 
            'Bottle', 'Contrast', 'Turtleneck', 'Wallet', 
            'Kaftan', 'Active Wear', 'Sweatshirt'
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

    df['Category'] = df['Item Name'].apply(get_category)
    
    # Group by Category and Price
    report = df.groupby(['Category', 'Item Cost']).agg({
        'Quantity': 'sum'
    }).reset_index()
    
    # Rename columns
    report.columns = ['Category', 'Price (TK)', 'Total Quantity Sold']
    
    # Calculate Total Amount
    report['Total Amount (TK)'] = report['Price (TK)'] * report['Total Quantity Sold']
    
    # Sort by Category and then Price
    report = report.sort_values(by=['Category', 'Price (TK)'])
    
    return report

if __name__ == "__main__":
    input_file = r'h:\Analysis\Product-Report\TestFile.xlsx'
    output_temp = r'h:\Analysis\Product-Report\Sales_Report.xlsx'
    
    report_df = generate_report(input_file)
    
    # Print the report
    print("CATEGORY WISE SALES REPORT")
    print("==========================")
    print(report_df.to_string(index=False))
    
    # Save to Excel
    report_df.to_excel(output_temp, index=False)
    print(f"\nReport successfully saved to: {output_temp}")
    
    # Also create a summary total for each category (optional but helpful)
    summary = report_df.groupby('Category').agg({
        'Total Quantity Sold': 'sum',
        'Total Amount (TK)': 'sum'
    }).reset_index()
    print("\nSUMMARY BY CATEGORY")
    print("===================")
    print(summary.to_string(index=False))
