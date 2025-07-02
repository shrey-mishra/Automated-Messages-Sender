import pandas as pd
df = pd.read_excel('data/MSME Supplier list.xlsx')
df['Phone '] = df['Phone '].apply(lambda x: f"+91{x}" if str(x).startswith(('9', '8', '7', '6')) and not str(x).startswith('+') else x)
df.to_excel('data/MSME Supplier list.xlsx', index=False)
print("Phone numbers after fixing:", df['Phone '].head(10).tolist())