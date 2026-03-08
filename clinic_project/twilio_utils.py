import logging
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

def send_whatsapp_welcome_message(to_number, patient_name):
    """
    Sends a WhatsApp welcome message to a new patient using Twilio.
    
    :param to_number: Patient's phone number (should be in E.164 format)
    :param patient_name: Name of the patient
    """
    try:
        # Ensure number starts with +
        if not to_number.startswith('+'):
            # Basic assumption: if no +, add it (though E.164 is preferred)
            # You might want to add country code default here if needed
            to_number = f"+{to_number.strip()}"
            
        whatsapp_to = f"whatsapp:{to_number}"
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message_body = f"Hello {patient_name}, welcome to our clinic! Your patient record has been successfully created."
        
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=whatsapp_to
        )
        
        logger.info(f"WhatsApp message sent to {to_number}. SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {to_number}: {str(e)}")
        # We don't want to crash the whole patient creation if SMS fails
        return None
