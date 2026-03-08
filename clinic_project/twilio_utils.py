from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_patient_whatsapp(phone_number, message):
    """
    Sends a WhatsApp message to a patient using Twilio.
    """
    try:
        # Ensure credentials are present
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_NUMBER]):
            logger.error("Twilio credentials missing in settings.")
            return False

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Format phone number if needed (assuming incoming is +...)
        to_number = f"whatsapp:{phone_number}" if not phone_number.startswith("whatsapp:") else phone_number

        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=to_number
        )

        logger.info(f"WhatsApp message sent successfully: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return False
