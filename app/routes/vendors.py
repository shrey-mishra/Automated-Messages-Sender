from fastapi import APIRouter, HTTPException
import sqlite3
from app.models import StatusUpdate

router = APIRouter()

@router.get("/vendors")
async def get_vendors():
    """Get all vendors."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vendors")
    vendors = c.fetchall()
    conn.close()
    
    return [
        {
            "vendor_account": v[0],
            "name": v[1],
            "email": v[2],
            "phone": v[3],
            "msme_status": v[4],
            "msme_category": v[5],
            "email_status": v[6],
            "whatsapp_status": v[7]
        } for v in vendors
    ]

@router.post("/update_status")
async def update_status(update: StatusUpdate):
    """Update vendor email or WhatsApp status."""
    if update.status not in ['Pending', 'Sent', 'Reverted']:
        raise HTTPException(status_code=400, detail="Invalid status")
    if update.status_type not in ['email_status', 'whatsapp_status']:
        raise HTTPException(status_code=400, detail="Invalid status_type")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute(f"UPDATE vendors SET {update.status_type} = ? WHERE vendor_account = ?", 
              (update.status, update.vendor_account))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Status updated successfully"}

@router.get("/status_counts")
async def get_status_counts():
    """Get email and WhatsApp status counts."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    
    # Get email status counts
    c.execute("SELECT email_status, COUNT(*) FROM vendors GROUP BY email_status")
    email_counts = c.fetchall()
    
    # Get whatsapp status counts  
    c.execute("SELECT whatsapp_status, COUNT(*) FROM vendors GROUP BY whatsapp_status")
    whatsapp_counts = c.fetchall()
    
    conn.close()
    
    # Format for frontend
    email_status = {"Pending": 0, "Sent": 0, "Reverted": 0}
    whatsapp_status = {"Pending": 0, "Sent": 0, "Reverted": 0}
    
    for status, count in email_counts:
        if status in email_status:
            email_status[status] = count
            
    for status, count in whatsapp_counts:
        if status in whatsapp_status:
            whatsapp_status[status] = count
    
    return {
        "email_status": email_status,
        "whatsapp_status": whatsapp_status
    }