import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

config = Config()