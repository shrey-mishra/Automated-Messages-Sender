from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import vendors, email, whatsapp, register
from app.database import init_db, load_excel_to_db
import logging
from dotenv import load_dotenv
import uvicorn
import argparse

# Load environment variables
load_dotenv()

# Configure logging (console and file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("Starting database initialization")
    init_db()
    logger.info("Loading Excel file")
    load_excel_to_db("data/MSME Supplier list.xlsx")
    logger.info("Starting Amber Email & WhatsApp Backend")
    yield
    logger.info("Shutting down Amber Email & WhatsApp Backend")

app = FastAPI(title="Amber Email & WhatsApp Backend", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(vendors.router, prefix="/api")
app.include_router(email.router, prefix="/api")
app.include_router(whatsapp.router, prefix="/api")
app.include_router(register.router, prefix="/api")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI server locally")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind (default: 8001)")
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)