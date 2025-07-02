from pydantic import BaseModel

class StatusUpdate(BaseModel):
    vendor_account: str
    status: str
    channel: str