"""Context processors for Smart Education Analytics."""


def global_template_context(request):
    """Add global variables to all templates."""
    context = {
        'unread_notifications': 0,
        'user_role': None,
    }

    if request.user.is_authenticated:
        # Unread notifications count
        try:
            from notifications.models import Notification
            context['unread_notifications'] = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            pass

        # User role
        try:
            context['user_role'] = request.user.profile.role
        except Exception:
            context['user_role'] = 'student'

    return context
