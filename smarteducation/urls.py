from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from dashboards.views import redirect_based_on_role
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(redirect_based_on_role), name='home'),
    path('dashboards/', include('dashboards.urls')),
    path('ml/', include('ml.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/v1/', include('api.urls')),
    path('', include('students.urls')),
    path('', include('accounts.urls')),
    path('advanced/', include('advanced_features.urls')),
    path('advanced_features/parent_portal/', RedirectView.as_view(url='/advanced/parent-portal/', permanent=False), name='parent_portal_legacy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)