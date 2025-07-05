from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from typing import Optional
import sqlite3
import os
from app.utils.validate_phone import validate_and_format_phone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs("uploads/certificates", exist_ok=True)

@router.post("/register_vendor")
async def register_vendor(
    vendor_code: str = Form(...),
    vendor_name: str = Form(...),
    msme_status: str = Form(...),
    msme_type: Optional[str] = Form(None),
    udyam_number: Optional[str] = Form(None),
    declaration_signed: Optional[bool] = Form(None),
    certificate: Optional[UploadFile] = File(None)
):
    """Register a new vendor."""
    try:
        # Validate required fields
        if not vendor_code or not vendor_name or not msme_status:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        if msme_status not in ['MSME', 'Non MSME']:
            raise HTTPException(status_code=400, detail="Invalid MSME status")
        
        # Validate MSME specific fields
        if msme_status == 'MSME':
            if not msme_type or not udyam_number:
                raise HTTPException(status_code=400, detail="MSME type and Udyam number required for MSME status")
            
            # Validate Udyam number format
            import re
            if not re.match(r'^UDYAM-[A-Z]{2}-\d{2}-\d{7}$', udyam_number):
                raise HTTPException(status_code=400, detail="Invalid Udyam number format")
        
        # Validate Non-MSME specific fields
        if msme_status == 'Non MSME':
            if not declaration_signed:
                raise HTTPException(status_code=400, detail="Declaration must be signed for Non-MSME status")
        
        # Handle certificate upload
        certificate_path = None
        if certificate:
            # Validate file type
            allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
            if certificate.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, PNG, and JPG files are allowed")
            
            # Save file
            file_extension = certificate.filename.split('.')[-1]
            certificate_filename = f"{vendor_code}_{udyam_number or 'cert'}.{file_extension}"
            certificate_path = f"uploads/certificates/{certificate_filename}"
            
            with open(certificate_path, "wb") as buffer:
                content = await certificate.read()
                buffer.write(content)
        
        # Check if vendor already exists
        conn = sqlite3.connect("vendors.db")
        c = conn.cursor()
        
        c.execute("SELECT vendor_account FROM vendors WHERE vendor_account = ?", (vendor_code,))
        if c.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Vendor code already exists")
        
        # Insert new vendor
        c.execute('''INSERT INTO vendors 
                     (vendor_account, name, email, phone, msme_status, msme_category, 
                      udyam_number, certificate_path, declaration_signed, email_status, whatsapp_status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (vendor_code, vendor_name, None, None, msme_status, msme_type,
                   udyam_number, certificate_path, declaration_signed, 'Pending', 'Pending'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"New vendor registered: {vendor_code} - {vendor_name}")
        
        return {
            "success": True,
            "message": "Vendor registered successfully",
            "data": {
                "vendor_code": vendor_code,
                "vendor_name": vendor_name,
                "msme_status": msme_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/check_vendor/{vendor_code}")
async def check_vendor_exists(vendor_code: str):
    """Check if vendor code already exists."""
    conn = sqlite3.connect("vendors.db")
    c = conn.cursor()
    c.execute("SELECT vendor_account FROM vendors WHERE vendor_account = ?", (vendor_code,))
    exists = c.fetchone() is not None
    conn.close()
    
    return {"exists": exists}