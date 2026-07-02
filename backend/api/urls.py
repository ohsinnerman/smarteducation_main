from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
# Core academic
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
# Advanced features
router.register(r'parents', views.ParentViewSet)
router.register(r'parent-links', views.ParentStudentLinkViewSet)
router.register(r'grade-forecasts', views.GradeForecastViewSet)
router.register(r'what-if', views.WhatIfScenarioViewSet)
router.register(r'learning-resources', views.LearningResourceViewSet)
router.register(r'learning-paths', views.LearningPathViewSet)
router.register(r'badges', views.BadgeViewSet)
router.register(r'student-badges', views.StudentBadgeViewSet)
router.register(r'points', views.StudentPointViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'ptm', views.ParentTeacherMeetingViewSet)
router.register(r'progress-reports', views.ProgressReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.me_api, name='me_api'),
    path('dashboard/admin/', views.admin_dashboard_api, name='admin_dashboard_api'),
    path('dashboard/teacher/', views.teacher_dashboard_api, name='teacher_dashboard_api'),
    path('dashboard/student/', views.student_dashboard_api, name='student_dashboard_api'),
    path('dashboard/parent/', views.parent_dashboard_api, name='parent_dashboard_api'),
    path('search/', views.search_api, name='search_api'),
]
