import pandas as pd

file_path = r'h:\Analysis\Product-Report\TestFile.xlsx'
df = pd.read_excel(file_path)
print("Columns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
