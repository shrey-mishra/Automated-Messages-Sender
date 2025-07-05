from pydantic import BaseModel

class StatusUpdate(BaseModel):
    vendor_account: str
    status_type: str  # 'email_status' or 'whatsapp_status'
    status: str       # 'Pending', 'Sent', 'Reverted'