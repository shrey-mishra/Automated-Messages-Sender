import logging
import re
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def validate_and_format_phone(phone) -> str:
    """Validate and format phone number to international format (e.g., +919811373733)."""
    if phone is None or str(phone).lower() == 'nan' or pd.isna(phone):
        logger.warning(f"Invalid phone number: {phone} (null or nan)")
        return None
    
    # Convert to string, handle scientific notation
    phone_str = str(int(float(phone))) if str(phone).replace('.', '', 1).isdigit() else str(phone)
    
    # Remove non-digits except +
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    
    # Handle multiple numbers (support //, /, ,, spaces)
    numbers = re.split(r'[/,\s]+', cleaned)
    for num in numbers:
        if num.startswith(('9', '8', '7', '6')) and not num.startswith('+'):
            num = f"+91{num}"
        if re.match(r'^\+\d{10,14}$', num):
            return num
    logger.warning(f"Invalid phone number format or length: {phone}")
    return None