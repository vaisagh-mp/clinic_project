import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Patient
from clinic_project.twilio_utils import send_whatsapp_welcome_message

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Patient)
def patient_created_welcome_message(sender, instance, created, **kwargs):
    """
    Signal receiver that sends a WhatsApp welcome message when a new Patient is created.
    """
    if created:
        patient_name = f"{instance.first_name} {instance.last_name}"
        phone_number = instance.phone_number
        
        if phone_number:
            logger.info(f"New patient created: {patient_name}. Triggering welcome message to {phone_number}.")
            send_whatsapp_welcome_message(phone_number, patient_name)
        else:
            logger.warning(f"New patient {patient_name} created without a phone number. Cannot send welcome message.")
