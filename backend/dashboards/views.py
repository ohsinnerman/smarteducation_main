from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Min, Q
from django.db.models.functions import TruncMonth, TruncWeek
from students.models import Student, Course, Subject, Result, AttendanceRecord, StudentEnrollment, Exam, Feedback
from accounts.models import UserProfile
from ml.models import PredictionResult
from notifications.models import Notification
import json


def get_role(request):
    """Helper to get the user's role."""
    try:
        return request.user.profile.role
    except (UserProfile.DoesNotExist, AttributeError):
        return 'student'


@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive analytics."""
    if get_role(request) not in ['admin']:
        return redirect_based_on_role(request)

    # Core stats
    total_students = Student.objects.filter(status='active').count()
    total_teachers = UserProfile.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    avg_attendance = Student.objects.filter(status='active').aggregate(
        avg=Avg('attendance'))['avg'] or 0
    avg_marks = Student.objects.filter(status='active').aggregate(
        avg=Avg('marks'))['avg'] or 0

    # User growth data (monthly registrations)
    user_growth = UserProfile.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    growth_labels = [ug['month'].strftime('%b %Y') for ug in user_growth if ug['month']]
    growth_values = [ug['count'] for ug in user_growth]

    # Grade distribution
    grade_distribution = Result.objects.values('grade').annotate(
        count=Count('id')
    ).order_by('grade')

    grade_labels = [gd['grade'] for gd in grade_distribution]
    grade_values = [gd['count'] for gd in grade_distribution]

    # Subject-wise performance
    subject_performance = Subject.objects.annotate(
        avg_marks=Avg('exams__results__marks_obtained')
    ).filter(avg_marks__isnull=False)

    subject_labels = [sp.name[:20] for sp in subject_performance]
    subject_values = [round(sp.avg_marks, 1) for sp in subject_performance]

    # Attendance distribution
    attendance_ranges = {
        '0-25%': Student.objects.filter(attendance__gte=0, attendance__lt=25).count(),
        '25-50%': Student.objects.filter(attendance__gte=25, attendance__lt=50).count(),
        '50-75%': Student.objects.filter(attendance__gte=50, attendance__lt=75).count(),
        '75-100%': Student.objects.filter(attendance__gte=75, attendance__lte=100).count(),
    }

    # At-risk students
    at_risk_students = PredictionResult.objects.filter(
        prediction_type='at_risk',
        predicted_value=1.0
    ).select_related('student')[:10]

    # Recent activity (latest results)
    recent_results = Result.objects.select_related('student', 'exam').order_by('-created_at')[:10]

    # Prediction accuracy
    prediction_accuracy = {
        'performance': PredictionResult.objects.filter(prediction_type='performance').aggregate(
            avg_confidence=Avg('confidence'))['avg_confidence'] or 0,
        'at_risk': PredictionResult.objects.filter(prediction_type='at_risk').aggregate(
            avg_confidence=Avg('confidence'))['avg_confidence'] or 0,
    }

    # Feedback stats
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    total_feedback = Feedback.objects.count()

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'avg_attendance': round(avg_attendance, 1),
        'avg_marks': round(avg_marks, 1),
        'at_risk_students': at_risk_students,
        'recent_results': recent_results,
        'avg_rating': round(avg_rating, 1),
        'total_feedback': total_feedback,
        # Chart data
        'growth_labels': json.dumps(growth_labels),
        'growth_values': json.dumps(growth_values),
        'grade_labels': json.dumps(grade_labels),
        'grade_values': json.dumps(grade_values),
        'subject_labels': json.dumps(subject_labels),
        'subject_values': json.dumps(subject_values),
        'attendance_labels': json.dumps(list(attendance_ranges.keys())),
        'attendance_values': json.dumps(list(attendance_ranges.values())),
        'prediction_accuracy': prediction_accuracy,
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard with course-focused analytics."""
    if get_role(request) != 'teacher':
        return redirect_based_on_role(request)

    teacher = request.user
    my_courses = Course.objects.filter(teacher=teacher)
    my_students = Student.objects.filter(
        enrollments__course__in=my_courses
    ).distinct()

    # Attendance trend
    attendance_trend = AttendanceRecord.objects.filter(
        student__in=my_students
    ).annotate(week=TruncWeek('date')).values('week').annotate(
        present=Count('id', filter=Q(status='present')),
        total=Count('id')
    ).order_by('week')[:12]

    attendance_labels = [at['week'].strftime('%b %d') if at['week'] else '' for at in attendance_trend]
    attendance_present = [at['present'] for at in attendance_trend]
    attendance_total = [at['total'] for at in attendance_trend]

    # Marks distribution for teacher's courses
    marks_data = Result.objects.filter(
        student__in=my_students,
        exam__subject__course__in=my_courses
    ).values('grade').annotate(count=Count('id')).order_by('grade')

    # At-risk in my courses
    at_risk_in_courses = PredictionResult.objects.filter(
        prediction_type='at_risk',
        predicted_value=1.0,
        student__in=my_students
    ).select_related('student')[:10]

    # Upcoming exams
    from datetime import date
    upcoming_exams = Exam.objects.filter(
        subject__course__in=my_courses,
        date__gte=date.today()
    ).order_by('date')[:5]

    # Feedback received
    my_feedback = Feedback.objects.filter(teacher=teacher).order_by('-created_at')[:10]
    avg_my_rating = Feedback.objects.filter(teacher=teacher).aggregate(
        avg=Avg('rating'))['avg'] or 0

    context = {
        'my_courses': my_courses,
        'my_students': my_students,
        'student_count': my_students.count(),
        'course_count': my_courses.count(),
        'at_risk_in_courses': at_risk_in_courses,
        'upcoming_exams': upcoming_exams,
        'my_feedback': my_feedback,
        'avg_my_rating': round(avg_my_rating, 1),
        'attendance_labels': json.dumps(attendance_labels),
        'attendance_present': json.dumps(attendance_present),
        'attendance_total': json.dumps(attendance_total),
        'marks_labels': json.dumps([md['grade'] for md in marks_data]),
        'marks_values': json.dumps([md['count'] for md in marks_data]),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'dashboards/teacher_dashboard.html', context)


@login_required
def dashboard_report_download(request):
    """Download a simple text report for the authenticated user."""
    role = get_role(request)
    report_lines = [
        'Smart Education Analytics Report',
        f'User: {request.user.username}',
        f'Role: {role}',
        'Status: Report generation successful.',
    ]
    response = HttpResponse('\n'.join(report_lines), content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="smart_education_report.txt"'
    return response


@login_required
def student_dashboard(request):
    """Student dashboard with personal performance analytics."""
    if get_role(request) != 'student':
        return redirect_based_on_role(request)

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None

    if not student:
        # Fallback for students without linked Student record
        context = {
            'student': None,
            'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        }
        return render(request, 'dashboards/student_dashboard.html', context)

    # My results
    my_results = Result.objects.filter(student=student).select_related('exam', 'exam__subject')
    my_attendance = AttendanceRecord.objects.filter(student=student)
    my_enrollments = StudentEnrollment.objects.filter(student=student, status='enrolled')

    # Attendance stats
    total_classes = my_attendance.count()
    present = my_attendance.filter(status='present').count()
    absent = my_attendance.filter(status='absent').count()
    late = my_attendance.filter(status='late').count()

    # Performance trend
    results_trend = my_results.order_by('created_at')
    trend_labels = [r.exam.name[:15] for r in results_trend]
    trend_values = [r.marks_obtained for r in results_trend]

    # Subject-wise marks
    subject_marks = my_results.values('exam__subject__name').annotate(
        avg_marks=Avg('marks_obtained')
    ).order_by('exam__subject__name')

    # Prediction
    my_prediction = PredictionResult.objects.filter(student=student).first()

    # Upcoming exams
    from datetime import date
    upcoming_exams = Exam.objects.filter(
        subject__course__in=student.enrollments.filter(status='enrolled').values('course'),
        date__gte=date.today()
    ).order_by('date')[:5]

    context = {
        'student': student,
        'my_results': my_results[:20],
        'my_enrollments': my_enrollments,
        'total_classes': total_classes,
        'present': present,
        'absent': absent,
        'late': late,
        'attendance_pct': student.attendance,
        'my_prediction': my_prediction,
        'upcoming_exams': upcoming_exams,
        'trend_labels': json.dumps(trend_labels),
        'trend_values': json.dumps(trend_values),
        'subject_labels': json.dumps([sm['exam__subject__name'] for sm in subject_marks]),
        'subject_values': json.dumps([round(sm['avg_marks'], 1) for sm in subject_marks]),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'dashboards/student_dashboard.html', context)


def redirect_based_on_role(request):
    """Redirect user to their appropriate dashboard."""
    role = get_role(request)
    if role == 'admin':
        from django.shortcuts import redirect
        return redirect('dashboards:admin_dashboard')
    elif role == 'teacher':
        from django.shortcuts import redirect
        return redirect('dashboards:teacher_dashboard')
    elif role == 'parent':
        from django.shortcuts import redirect
        return redirect('advanced_features:parent_portal')
    else:
        from django.shortcuts import redirect
        return redirect('dashboards:student_dashboard')
