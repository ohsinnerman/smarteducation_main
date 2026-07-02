from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification
from .config import email_configured


def send_email_notification(user, title, message):
    """Send an email notification to a user."""
    ok, reason = email_configured()
    if not ok:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='email',
            status='failed',
        )
        return False
    try:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@smarteducation.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='email',
            status='sent',
        )
        return True
    except Exception as e:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='email',
            status='failed',
        )
        return False


def send_welcome_email(user):
    """Send welcome email to new user."""
    title = "Welcome to Smart Education Analytics Platform"
    message = f"Hello {user.username},\n\nWelcome to the Smart Education Analytics Platform! Your account has been created successfully.\n\nBest regards,\nSmart Education Team"
    return send_email_notification(user, title, message)


def send_at_risk_alert(user, student_name, risk_level):
    """Send at-risk student alert."""
    title = f"At-Risk Alert: {student_name}"
    message = f"Student {student_name} has been identified as {risk_level} risk. Please review their performance and consider intervention strategies."
    return send_email_notification(user, title, message)


def send_exam_result_notification(user, student_name, exam_name, marks, grade):
    """Send exam result notification."""
    title = f"Result Published: {exam_name}"
    message = f"Results for {exam_name} have been published. Student {student_name} scored {marks} marks (Grade: {grade})."
    return send_email_notification(user, title, message)


def send_attendance_warning(user, student_name, attendance_pct):
    """Send low attendance warning."""
    title = f"Low Attendance Warning: {student_name}"
    message = f"Student {student_name} has attendance of {attendance_pct}%, which is below the required threshold."
    return send_email_notification(user, title, message)
