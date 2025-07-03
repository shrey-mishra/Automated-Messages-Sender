import pandas as pd
import re
import numpy as np

def clean_phone(phone):
    if pd.isna(phone) or str(phone).lower() == 'nan':
        return None, "Null or NaN"
    phone_str = str(int(float(phone))) if str(phone).replace('.', '', 1).isdigit() else str(phone)
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    numbers = cleaned.split('//')
    for num in numbers:
        if num.startswith(('9', '8', '7', '6')) and not num.startswith('+'):
            num = f"+91{num}"
        if num.startswith('+') and 12 <= len(num) <= 15:
            return num, None
    return None, f"Invalid format or length: {phone}"

df = pd.read_excel('data/MSME Supplier list.xlsx')
results = df[['Vendor account', 'Name', 'Phone ']].copy()
results['Cleaned Phone'], results['Error'] = zip(*results['Phone '].apply(clean_phone))
invalid = results[results['Cleaned Phone'].isna()]
print(f"Invalid phone numbers: {len(invalid)}")
print("Invalid entries (first 10):")
print(invalid[['Vendor account', 'Name', 'Phone ', 'Error']].head(10))
invalid.to_csv('data/invalid_phones.csv', index=False)
df['Phone '] = results['Cleaned Phone']
df.to_excel('data/MSME Supplier list.xlsx', index=False)
print("Sample phone numbers:", df['Phone '].head(10).tolist())