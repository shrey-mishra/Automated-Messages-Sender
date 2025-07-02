from fastapi import APIRouter, HTTPException
import sqlite3
from app.email_service import send_emails_in_batches

router = APIRouter()

@router.post("/send_emails")
async def send_emails():
    """Send emails to vendors with Pending status."""
    logger = logging.getLogger(__name__)
    logger.info("Starting email sending process for 2211 vendors")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT name, email, vendor_account FROM vendors WHERE email_status = 'Pending'")
# No change needed here, as it uses database column 'email', not Excel's 'Email '
    vendors = c.fetchall()
    conn.close()
    
    if not vendors:
        logger.info("No pending emails to send")
        return {"results": []}
    
    try:
        results = await send_emails_in_batches(vendors)
        logger.info(f"Email sending completed: {len(results)} emails processed")
        
        # Update database with Sent statuses
        conn = sqlite3.connect("vendors.db")
        c = conn.cursor()
        for result in results:
            if result["status"] == "Sent":
                c.execute("UPDATE vendors SET email_status = 'Sent' WHERE vendor_account = ?", 
                          (result["vendor_account"],))
        conn.commit()
        conn.close()
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise HTTPException(status_code=500, detail="Email sending failed")