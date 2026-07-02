from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'attendance', views.AttendanceRecordViewSet)
router.register(r'enrollments', views.StudentEnrollmentViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'notification-preferences', views.NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'predictions', views.PredictionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/admin/', views.admin_dashboard_api, name='admin_dashboard_api'),
    path('search/', views.search_api, name='search_api'),
]
