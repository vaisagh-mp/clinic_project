from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_patient_whatsapp(phone_number, message, media_urls=None):
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

        kwargs = {
            "from_": settings.TWILIO_WHATSAPP_NUMBER,
            "body": message,
            "to": to_number
        }
        if media_urls:
            kwargs["media_url"] = media_urls

        message_obj = client.messages.create(**kwargs)

        logger.info(f"WhatsApp message sent successfully: {message_obj.sid}")
        return True
    except Exception as e:
        # Log the exact Twilio error (includes error code and message)
        error_msg = getattr(e, 'msg', None) or str(e)
        error_code = getattr(e, 'code', None)
        logger.error(f"Failed to send WhatsApp message. Code={error_code}, Reason={error_msg}")
        print(f"[TWILIO ERROR] Code={error_code} | Reason={error_msg}")
        return False
