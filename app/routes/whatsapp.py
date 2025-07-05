from fastapi import APIRouter, HTTPException
import sqlite3
import logging
from app.whatsapp_service import send_whatsapp_messages_in_batches

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send_whatsapp_messages")
async def send_whatsapp_messages():
    """Send WhatsApp messages to vendors with Pending status."""
    logger.info("Starting WhatsApp message sending process")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT name, phone, vendor_account FROM vendors WHERE whatsapp_status = 'Pending'")
    vendors = c.fetchall()
    conn.close()
    
    if not vendors:
        logger.info("No pending WhatsApp messages to send")
        return {
            "success": True,
            "message": "No pending WhatsApp messages to send",
            "count": 0
        }
    
    try:
        results = await send_whatsapp_messages_in_batches(vendors)
        sent_count = sum(1 for r in results if r["status"] == "Sent")
        
        # Update database with Sent statuses
        conn = sqlite3.connect("vendors.db")
        c = conn.cursor()
        for result in results:
            if result["status"] == "Sent":
                c.execute("UPDATE vendors SET whatsapp_status = 'Sent' WHERE vendor_account = ?", 
                          (result["vendor_account"],))
        conn.commit()
        conn.close()
        
        logger.info(f"WhatsApp message sending completed: {sent_count} messages sent")
        return {
            "success": True,
            "message": f"Successfully sent {sent_count} WhatsApp messages",
            "count": sent_count
        }
        
    except Exception as e:
        logger.error(f"WhatsApp message sending failed: {e}")
        return {
            "success": False,
            "message": f"WhatsApp message sending failed: {str(e)}",
            "count": 0
        }