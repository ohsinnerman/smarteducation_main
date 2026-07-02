from django.conf import settings
from .models import Notification


def send_sms_notification(user, message):
    """Send SMS notification using Twilio."""
    try:
        from twilio.rest import Client

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            Notification.objects.create(
                user=user,
                title='SMS Notification',
                message=message,
                notification_type='sms',
                status='failed',
            )
            return False

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Get user's phone number from profile
        phone = getattr(user.profile, 'phone', None)
        if not phone:
            return False

        message_obj = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )

        Notification.objects.create(
            user=user,
            title='SMS Notification',
            message=message,
            notification_type='sms',
            status='sent',
        )
        return True

    except Exception as e:
        Notification.objects.create(
            user=user,
            title='SMS Notification',
            message=message,
            notification_type='sms',
            status='failed',
        )
        return False


def send_sms_at_risk_alert(user, student_name, risk_level):
    """Send SMS for at-risk student."""
    message = f"ALERT: Student {student_name} identified as {risk_level} risk. - Smart Education Platform"
    return send_sms_notification(user, message)


def send_sms_exam_reminder(user, exam_name, exam_date):
    """Send SMS exam reminder."""
    message = f"Reminder: {exam_name} is scheduled on {exam_date}. - Smart Education Platform"
    return send_sms_notification(user, message)
