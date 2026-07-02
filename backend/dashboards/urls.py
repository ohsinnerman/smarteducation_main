from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboards/student/', permanent=False), name='dashboard_root'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('report/download/', views.dashboard_report_download, name='dashboard_report_download'),
]
