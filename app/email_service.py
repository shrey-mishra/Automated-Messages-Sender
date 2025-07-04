from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import asyncio
import logging
from app.config import config
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def send_email(to_email: str, vendor_name: str) -> bool:
    subject = "Request for MSME Supplier Data and Updated Udyam Certificate by 5th July 2025"
    body = f"""Dear {vendor_name},

Greetings from Amber Group!!

As part of our compliance requirements, please provide by 5th July 2025:
1. Supplier Category (e.g., Micro, Small, Medium).
2. Latest Udyam Registration Certificate.
3. If none, submit a declaration.

Upload details here: [Insert Upload Link Here]

Contact:
Mr. Karan Nanda (6280058216)
Mr. Abhishek Sharma (8448760560)

Best regards,
Amber Group"""

    message = Mail(
        from_email=config.FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(config.SENDGRID_API_KEY)
        response = await asyncio.to_thread(sg.send, message)
        logger.info(f"Email sent to {to_email}: {response.status_code}")
        return response.status_code in [200, 202]
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False

async def send_emails_in_batches(vendors, batch_size=20):
    results = []
    for i in range(0, len(vendors), batch_size):
        batch = vendors[i:i + batch_size]
        tasks = [send_email(email, name) for name, email, _ in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (name, email, vendor_account), result in zip(batch, batch_results):
            status = "Sent" if result is True else "Failed"
            results.append({"vendor_account": vendor_account, "email": email, "status": status})
        
        await asyncio.sleep(1)
        logger.info(f"Processed email batch {i//batch_size + 1}: {len(batch)} emails")
    
    return results