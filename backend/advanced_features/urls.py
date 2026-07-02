
from django.urls import path
from . import views

app_name = 'advanced_features'

urlpatterns = [
    path('grade-forecast/', views.grade_forecast_view, name='grade_forecast'),
    path('learning-path/', views.learning_path_view, name='learning_path'),
    path('gamification/', views.gamification_view, name='gamification'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('parent-portal/', views.parent_portal_view, name='parent_portal'),
    path('progress-report/<int:student_id>/', views.progress_report_view, name='progress_report'),
    path('ptm-scheduler/', views.ptm_scheduler_view, name='ptm_scheduler'),
]
