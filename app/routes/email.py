from fastapi import APIRouter, HTTPException
import sqlite3
import logging
from app.email_service import send_emails_in_batches

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send_emails")
async def send_emails():
    """Send emails to vendors with Pending status."""
    logger.info("Starting email sending process")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT name, email, vendor_account FROM vendors WHERE email_status = 'Pending'")
    vendors = c.fetchall()
    conn.close()
    
    if not vendors:
        logger.info("No pending emails to send")
        return {
            "success": True,
            "message": "No pending emails to send",
            "count": 0
        }
    
    try:
        results = await send_emails_in_batches(vendors)
        sent_count = sum(1 for r in results if r["status"] == "Sent")
        
        # Update database with Sent statuses
        conn = sqlite3.connect("vendors.db")
        c = conn.cursor()
        for result in results:
            if result["status"] == "Sent":
                c.execute("UPDATE vendors SET email_status = 'Sent' WHERE vendor_account = ?", 
                          (result["vendor_account"],))
        conn.commit()
        conn.close()
        
        logger.info(f"Email sending completed: {sent_count} emails sent")
        return {
            "success": True,
            "message": f"Successfully sent {sent_count} emails",
            "count": sent_count
        }
        
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return {
            "success": False,
            "message": f"Email sending failed: {str(e)}",
            "count": 0
        }