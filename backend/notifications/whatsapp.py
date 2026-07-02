from django.conf import settings
from .models import Notification


def send_whatsapp_notification(user, message):
    """Send WhatsApp notification using Twilio WhatsApp Business API."""
    try:
        from twilio.rest import Client

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            Notification.objects.create(
                user=user,
                title='WhatsApp Notification',
                message=message,
                notification_type='whatsapp',
                status='failed',
            )
            return False

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Get user's phone number from profile
        phone = getattr(user.profile, 'phone', None)
        if not phone:
            return False

        # WhatsApp requires the 'whatsapp:' prefix
        whatsapp_from = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"
        whatsapp_to = f"whatsapp:{phone}"

        message_obj = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=whatsapp_to,
        )

        Notification.objects.create(
            user=user,
            title='WhatsApp Notification',
            message=message,
            notification_type='whatsapp',
            status='sent',
        )
        return True

    except Exception as e:
        Notification.objects.create(
            user=user,
            title='WhatsApp Notification',
            message=message,
            notification_type='whatsapp',
            status='failed',
        )
        return False


def send_whatsapp_at_risk_alert(user, student_name, risk_level):
    """Send WhatsApp at-risk alert."""
    message = f"*At-Risk Alert*\nStudent: {student_name}\nRisk Level: {risk_level}\nPlease review and take necessary action.\n\n- Smart Education Platform"
    return send_whatsapp_notification(user, message)


def send_whatsapp_monthly_report(user, student_name, attendance, marks):
    """Send WhatsApp monthly report summary."""
    message = f"*Monthly Report - {student_name}*\nAttendance: {attendance}%\nMarks: {marks}\n\n- Smart Education Platform"
    return send_whatsapp_notification(user, message)
