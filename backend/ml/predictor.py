import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import joblib
from django.conf import settings
from django.db.models import Avg, Max, Min, Count
from students.models import Student, Result, AttendanceRecord, StudentEnrollment
from .models import PredictionResult


MODEL_DIR = os.path.join(settings.BASE_DIR, 'smarteducation', 'ml', 'saved_models')
os.makedirs(MODEL_DIR, exist_ok=True)


def get_student_features(student):
    """Extract feature vector for a student."""
    results = Result.objects.filter(student=student)
    attendance_records = AttendanceRecord.objects.filter(student=student)

    total_exams = results.count()
    avg_marks = results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
    max_marks = results.aggregate(max=Max('marks_obtained'))['max'] or 0
    min_marks = results.aggregate(min=Min('marks_obtained'))['min'] or 0

    total_classes = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    late_count = attendance_records.filter(status='late').count()
    attendance_pct = (present_count + late_count * 0.5) / total_classes * 100 if total_classes > 0 else 0

    # Trend: compare first half vs second half marks
    marks_list = list(results.order_by('created_at').values_list('marks_obtained', flat=True))
    if len(marks_list) >= 2:
        half = len(marks_list) // 2
        first_half_avg = np.mean(marks_list[:half])
        second_half_avg = np.mean(marks_list[half:])
        marks_trend = second_half_avg - first_half_avg
    else:
        marks_trend = 0

    return {
        'total_exams': total_exams,
        'avg_marks': avg_marks,
        'max_marks': max_marks,
        'min_marks': min_marks,
        'attendance_pct': attendance_pct,
        'marks_trend': marks_trend,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': total_classes - present_count - late_count,
    }


def prepare_training_data():
    """Prepare dataset from all students for training."""
    students = Student.objects.filter(status='active')
    features_list = []
    labels_performance = []
    labels_at_risk = []

    for student in students:
        feat = get_student_features(student)
        features_list.append(feat)

        # Performance label: use current marks as target
        labels_performance.append(student.marks)

        # At-risk label: attendance < 60 or marks < 40
        is_at_risk = 1 if (feat['attendance_pct'] < 60 or student.marks < 40) else 0
        labels_at_risk.append(is_at_risk)

    df = pd.DataFrame(features_list)
    return df, np.array(labels_performance), np.array(labels_at_risk)


def train_models():
    """Train and save ML models."""
    df, labels_performance, labels_at_risk = prepare_training_data()

    if len(df) < 5:
        return {'error': 'Not enough data to train models. Need at least 5 students with data.'}

    metrics = {}

    # Performance Prediction Model (Gradient Boosting Regressor)
    X_train, X_test, y_train, y_test = train_test_split(df, labels_performance, test_size=0.2, random_state=42)

    perf_model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    perf_model.fit(X_train, y_train)
    y_pred = perf_model.predict(X_test)

    metrics['performance'] = {
        'r2_score': round(r2_score(y_test, y_pred), 4),
        'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        'samples': len(df),
    }

    joblib.dump(perf_model, os.path.join(MODEL_DIR, 'performance_model.pkl'))

    # At-Risk Detection Model (Random Forest Classifier)
    X_train, X_test, y_train, y_test = train_test_split(df, labels_at_risk, test_size=0.2, random_state=42)

    risk_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    risk_model.fit(X_train, y_train)
    y_pred = risk_model.predict(X_test)

    metrics['at_risk'] = {
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'samples': len(df),
    }

    joblib.dump(risk_model, os.path.join(MODEL_DIR, 'at_risk_model.pkl'))

    return metrics


def predict_student_performance(student):
    """Predict performance for a single student."""
    model_path = os.path.join(MODEL_DIR, 'performance_model.pkl')
    if not os.path.exists(model_path):
        # Fallback: use current marks as prediction
        return round(student.marks, 2), 0.85

    model = joblib.load(model_path)
    feat = get_student_features(student)
    df = pd.DataFrame([feat])
    prediction = model.predict(df)[0]
    confidence = 0.85
    try:
        score_val = model.score(df, [student.marks]) if hasattr(model, 'score') else 0.8
        if score_val is not None and not (score_val != score_val):  # check not NaN
            confidence = min(score_val, 1.0)
    except Exception:
        pass

    return round(prediction, 2), round(confidence, 4)


def predict_at_risk(student):
    """Predict if a student is at risk."""
    model_path = os.path.join(MODEL_DIR, 'at_risk_model.pkl')
    if not os.path.exists(model_path):
        # Fallback: simple rule-based
        is_at_risk = student.attendance < 60 or student.marks < 40
        confidence = 0.9 if is_at_risk else 0.85
        risk_level = 'high' if is_at_risk else 'low'
        return is_at_risk, confidence, risk_level

    model = joblib.load(model_path)
    feat = get_student_features(student)
    df = pd.DataFrame([feat])
    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]

    confidence = round(max(probabilities), 4)
    risk_level = 'high' if prediction == 1 and confidence > 0.7 else 'medium' if prediction == 1 else 'low'

    return bool(prediction), confidence, risk_level


def run_predictions_for_all():
    """Run predictions for all active students and save results."""
    students = Student.objects.filter(status='active')
    results_count = 0

    for student in students:
        # Performance prediction
        perf_result = predict_student_performance(student)
        if perf_result:
            predicted_value, confidence = perf_result
            PredictionResult.objects.update_or_create(
                student=student,
                prediction_type='performance',
                defaults={
                    'predicted_value': predicted_value,
                    'confidence': confidence,
                }
            )
            results_count += 1

        # At-risk prediction
        risk_result = predict_at_risk(student)
        if risk_result:
            is_at_risk, confidence, risk_level = risk_result
            PredictionResult.objects.update_or_create(
                student=student,
                prediction_type='at_risk',
                defaults={
                    'predicted_value': float(is_at_risk),
                    'confidence': confidence,
                    'risk_level': risk_level,
                }
            )
            results_count += 1

    return results_count
