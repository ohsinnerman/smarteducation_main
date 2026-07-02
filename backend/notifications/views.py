from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, NotificationPreference


@login_required
def notification_list(request):
    """View all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = Notification.objects.get(pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:notification_list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')


@login_required
def unread_count_api(request):
    """API endpoint to get unread notification count."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
def notification_preferences(request):
    """View and update notification preferences."""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        prefs.email_enabled = request.POST.get('email_enabled') == 'on'
        prefs.sms_enabled = request.POST.get('sms_enabled') == 'on'
        prefs.whatsapp_enabled = request.POST.get('whatsapp_enabled') == 'on'
        prefs.in_app_enabled = request.POST.get('in_app_enabled') == 'on'
        prefs.save()
        return redirect('notifications:notification_preferences')

    context = {
        'preferences': prefs,
    }
    return render(request, 'notifications/preferences.html', context)
