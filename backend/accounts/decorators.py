from functools import wraps
from django.shortcuts import redirect
from django.conf import settings


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
            if user_role not in allowed_roles:
                return redirect('home')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
