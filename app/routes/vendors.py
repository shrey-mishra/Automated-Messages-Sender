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
    if update.channel not in ['email', 'whatsapp']:
        raise HTTPException(status_code=400, detail="Invalid channel")
    
    column = "email_status" if update.channel == "email" else "whatsapp_status"
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute(f"UPDATE vendors SET {column} = ? WHERE vendor_account = ?", 
              (update.status, update.vendor_account))
    conn.commit()
    conn.close()
    
    return {"vendor_account": update.vendor_account, "status": update.status, "channel": update.channel}

@router.get("/status_counts")
async def get_status_counts():
    """Get email and WhatsApp status counts."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT email_status, COUNT(*) FROM vendors GROUP BY email_status")
    email_counts = c.fetchall()
    c.execute("SELECT whatsapp_status, COUNT(*) FROM vendors GROUP BY whatsapp_status")
    whatsapp_counts = c.fetchall()
    conn.close()
    
    return {
        "email": {"labels": [row[0] for row in email_counts], "data": [row[1] for row in email_counts]},
        "whatsapp": {"labels": [row[0] for row in whatsapp_counts], "data": [row[1] for row in whatsapp_counts]}
    }