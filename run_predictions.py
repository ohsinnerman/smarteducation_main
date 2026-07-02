
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()

from ml.predictor import train_models, run_predictions_for_all, predict_student_performance, predict_at_risk
from students.models import Student

print("Training models...")
train_result = train_models()
print(train_result)
print("\nTesting single prediction...")
students = Student.objects.filter(status='active')[:1]
for student in students:
    print(f"Student: {student.name}")
    perf = predict_student_performance(student)
    print(f"  Performance: {perf}")
    risk = predict_at_risk(student)
    print(f"  Risk: {risk}")
print("\nRunning predictions for all students...")
pred_count = run_predictions_for_all()
print(f"Generated {pred_count} predictions!")
