from twilio.rest import Client
import asyncio
import logging
from app.config import config

logger = logging.getLogger(__name__)

async def send_whatsapp_message(client: Client, to_phone: str, vendor_name: str) -> bool:
    """Send WhatsApp message using Twilio."""
    body = f"""Dear {vendor_name},

Greetings from Amber Group!!

As part of our compliance requirements, please provide by 5th July 2025:
1. Supplier Category (e.g., Micro, Small, Medium).
2. Latest Udyam Registration Certificate.
3. If none, submit a declaration.

Upload details here: [Insert Upload Link Here]

Contact:
Mr. Karan Nanda (6280058216)
Mr. Abhishek Sharma (8448760560)"""

    try:
        message = await asyncio.to_thread(
            client.messages.create,
            from_=f"whatsapp:{config.WHATSAPP_PHONE_NUMBER}",
            body=body,
            to=f"whatsapp:{to_phone}"
        )
        logger.info(f"WhatsApp message sent to {to_phone}: {message.sid}")
        return message.status in ["queued", "sent", "delivered"]
    except Exception as e:
        logger.error(f"Error sending WhatsApp message to {to_phone}: {e}")
        return False

async def send_whatsapp_messages_in_batches(vendors, batch_size=20):
    """Send WhatsApp messages in batches using Twilio."""
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")
        raise

    results = []
    for i in range(0, len(vendors), batch_size):
        batch = vendors[i:i + batch_size]
        tasks = [send_whatsapp_message(client, phone, name) for name, phone, _ in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (name, phone, vendor_account), result in zip(batch, batch_results):
            status = "Sent" if result is True else "Failed"
            results.append({"vendor_account": vendor_account, "phone": phone, "status": status})
        
        await asyncio.sleep(1)  # Rate limiting
        logger.info(f"Processed WhatsApp batch {i//batch_size + 1}: {len(batch)} messages")
    
    return results