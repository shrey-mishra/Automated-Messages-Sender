import sqlite3
import pandas as pd
import logging
from app.utils.validate_phone import validate_and_format_phone

logger = logging.getLogger(__name__)

def init_db():
    """Initialize SQLite database with email and WhatsApp status."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vendors
                 (vendor_account TEXT PRIMARY KEY, name TEXT, email TEXT, phone TEXT,
                  msme_status TEXT, msme_category TEXT, email_status TEXT, whatsapp_status TEXT)''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def load_excel_to_db(excel_path="data/MSME Supplier list.xlsx"):
    """Load Excel data into SQLite database with phone validation."""
    logger.info("Loading Excel file into database")
    df = pd.read_excel(excel_path)
    if len(df) != 2211:
        logger.warning(f"Expected 2211 vendors, found {len(df)}")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    invalid_phones = 0
    for _, row in df.iterrows():
        phone = validate_and_format_phone(str(row['Phone ']))  # Updated column name
        if phone is None:
            invalid_phones += 1
            continue
        c.execute('''INSERT OR REPLACE INTO vendors
                     (vendor_account, name, email, phone, msme_status, msme_category, email_status, whatsapp_status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (row['Vendor account'], row['Name'], row['Email '], phone,
                   row['Current Msme Staus '], row['MSME Category'], 'Pending', 'Pending'))  # Updated column names
    conn.commit()
    conn.close()
    if invalid_phones > 0:
        logger.warning(f"Skipped {invalid_phones} vendors due to invalid phone numbers")
    logger.info("Excel data loaded successfully")