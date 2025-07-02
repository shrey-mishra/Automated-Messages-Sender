from fastapi import FastAPI
from app.routes import vendors, email, whatsapp
from app.database import init_db, load_excel_to_db
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Amber Email & WhatsApp Backend", version="1.0.0")

# Include route modules
app.include_router(vendors.router, prefix="/api")
app.include_router(email.router, prefix="/api")
app.include_router(whatsapp.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    init_db()
    load_excel_to_db("data/vendors.xlsx")
    logger.info("Starting Amber Email & WhatsApp Backend")