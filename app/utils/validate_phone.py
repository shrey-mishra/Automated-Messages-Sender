import logging
import re

logger = logging.getLogger(__name__)

def validate_and_format_phone(phone: str) -> str:
    """Validate and format phone number to international format (e.g., +919811373733)."""
    # Remove non-digits except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Ensure starts with +
    if not cleaned.startswith('+'):
        # Assume Indian numbers if no country code (based on example +919811373733)
        if cleaned.startswith('9') or cleaned.startswith('8') or cleaned.startswith('7') or cleaned.startswith('6'):
            cleaned = '+91' + cleaned
        else:
            logger.warning(f"Invalid phone number format: {phone}")
            return None
    
    # Validate length (e.g., +91 followed by 10 digits)
    if len(cleaned) < 12 or len(cleaned) > 15:
        logger.warning(f"Invalid phone number length: {phone}")
        return None
    
    return cleaned