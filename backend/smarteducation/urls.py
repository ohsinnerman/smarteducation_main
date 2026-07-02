"""
Backend is now API-only. The end-user UI is the separate React frontend; Django
serves the REST API and the admin site (kept for staff/ops). The old
template-rendering routes were removed with their templates in the frontend/
backend split.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Lightweight health/root so hitting the bare host doesn't 404.
    path('', lambda r: JsonResponse({'service': 'smarteducation-api', 'status': 'ok'})),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
