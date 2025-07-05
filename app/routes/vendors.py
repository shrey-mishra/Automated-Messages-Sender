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
    
    return {
        "success": True,
        "data": [
            {
                "vendor_account": v[0],
                "name": v[1],
                "email": v[2],
                "phone": v[3],
                "msme_status": v[4],
                "msme_category": v[5],
                "udyam_number": v[6],
                "certificate_path": v[7],
                "declaration_signed": v[8],
                "email_status": v[9],
                "whatsapp_status": v[10]
            } for v in vendors
        ]
    }

@router.post("/update_status")
async def update_status(data: dict):
    """Update vendor email or WhatsApp status."""
    vendor_account = data.get("vendor_account")
    status_type = data.get("status_type")
    status = data.get("status")
    
    if status not in ['Pending', 'Sent', 'Reverted']:
        raise HTTPException(status_code=400, detail="Invalid status")
    if status_type not in ['email_status', 'whatsapp_status']:
        raise HTTPException(status_code=400, detail="Invalid status type")
    
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute(f"UPDATE vendors SET {status_type} = ? WHERE vendor_account = ?", 
              (status, vendor_account))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "Status updated successfully"
    }

@router.get("/status_counts")
async def get_status_counts():
    """Get email and WhatsApp status counts."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    
    # Get email status counts
    c.execute("SELECT email_status, COUNT(*) FROM vendors GROUP BY email_status")
    email_counts = dict(c.fetchall())
    
    # Get whatsapp status counts  
    c.execute("SELECT whatsapp_status, COUNT(*) FROM vendors GROUP BY whatsapp_status")
    whatsapp_counts = dict(c.fetchall())
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "email_status": {
                "Pending": email_counts.get("Pending", 0),
                "Sent": email_counts.get("Sent", 0),
                "Reverted": email_counts.get("Reverted", 0)
            },
            "whatsapp_status": {
                "Pending": whatsapp_counts.get("Pending", 0),
                "Sent": whatsapp_counts.get("Sent", 0),
                "Reverted": whatsapp_counts.get("Reverted", 0)
            }
        }
    }