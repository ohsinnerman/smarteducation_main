from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('', views.ml_dashboard, name='ml_dashboard'),
    path('train/', views.train_model_view, name='train_model'),
    path('predict/', views.run_predictions_view, name='run_predictions'),
    path('student/<int:student_id>/', views.student_prediction_detail, name='student_prediction'),
]
