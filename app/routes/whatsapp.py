from fastapi import APIRouter, HTTPException
import sqlite3
from app.whatsapp_service import send_whatsapp_messages_in_batches
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send_whatsapp_messages")
async def send_whatsapp_messages():
    """Send WhatsApp messages to vendors with Pending status."""
    logger.info("Starting WhatsApp message sending process for 2211 vendors")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT name, phone, vendor_account FROM vendors WHERE whatsapp_status = 'Pending'")
    vendors = c.fetchall()
    conn.close()
    
    if not vendors:
        logger.info("No pending WhatsApp messages to send")
        return {"results": []}
    
    try:
        results = await send_whatsapp_messages_in_batches(vendors)
        logger.info(f"WhatsApp message sending completed: {len(results)} messages processed")
        
        # Update database with Sent statuses
        conn = sqlite3.connect("vendors.db")
        c = conn.cursor()
        for result in results:
            if result["status"] == "Sent":
                c.execute("UPDATE vendors SET whatsapp_status = 'Sent' WHERE vendor_account = ?", 
                          (result["vendor_account"],))
        conn.commit()
        conn.close()
        
        return {"results": results}
    except Exception as e:
        logger.error(f"WhatsApp message sending failed: {e}")
        raise HTTPException(status_code=500, detail="WhatsApp message sending failed")