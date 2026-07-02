from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils import timezone

from students.models import Student, Course, Subject, Exam, Result, AttendanceRecord, StudentEnrollment, Feedback
from notifications.models import Notification, NotificationPreference
from ml.models import PredictionResult
from accounts.models import UserProfile
from advanced_features.models import (
    Parent, ParentStudentLink, GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath, Badge, StudentBadge,
    StudentPoint, Event, ParentTeacherMeeting, ProgressReport,
)

from .permissions import IsAdmin, IsTeacherOrAdmin, ReadOnlyOrTeacher
from .serializers import (
    UserSerializer, StudentSerializer, CourseSerializer, SubjectSerializer,
    ExamSerializer, ResultSerializer, AttendanceRecordSerializer,
    StudentEnrollmentSerializer, FeedbackSerializer, NotificationSerializer,
    NotificationPreferenceSerializer, PredictionResultSerializer,
    ParentSerializer, ParentStudentLinkSerializer, GradeForecastSerializer,
    WhatIfScenarioSerializer, LearningResourceSerializer,
    PersonalizedLearningPathSerializer, BadgeSerializer, StudentBadgeSerializer,
    StudentPointSerializer, EventSerializer, ParentTeacherMeetingSerializer,
    ProgressReportSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('name')
    serializer_class = StudentSerializer
    filterset_fields = ('program', 'year', 'status')
    search_fields = ('name', 'roll_number')


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ('teacher',)
    search_fields = ('name', 'code')


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filterset_fields = ('course',)
    search_fields = ('name', 'code')


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    filterset_fields = ('exam_type', 'subject')
    search_fields = ('name',)


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all().order_by('-id')
    serializer_class = ResultSerializer
    filterset_fields = ('student', 'exam', 'grade')
    search_fields = ('student__name',)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all().order_by('-date')
    serializer_class = AttendanceRecordSerializer
    filterset_fields = ('student', 'subject', 'status', 'date')
    search_fields = ('student__name',)


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all().order_by('-id')
    serializer_class = StudentEnrollmentSerializer
    filterset_fields = ('student', 'course', 'status')


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-id')
    serializer_class = FeedbackSerializer
    filterset_fields = ('student', 'teacher', 'rating')


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredictionResult.objects.all()
    serializer_class = PredictionResultSerializer
    filterset_fields = ('student', 'prediction_type', 'risk_level')


# --- advanced_features viewsets ---------------------------------------------

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsTeacherOrAdmin]


class ParentStudentLinkViewSet(viewsets.ModelViewSet):
    queryset = ParentStudentLink.objects.all()
    serializer_class = ParentStudentLinkSerializer
    permission_classes = [IsTeacherOrAdmin]
    filterset_fields = ('parent', 'student')


class GradeForecastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GradeForecast.objects.all()
    serializer_class = GradeForecastSerializer
    filterset_fields = ('student', 'subject')


class WhatIfScenarioViewSet(viewsets.ModelViewSet):
    queryset = WhatIfScenario.objects.all()
    serializer_class = WhatIfScenarioSerializer
    filterset_fields = ('student', 'subject')


class LearningResourceViewSet(viewsets.ModelViewSet):
    queryset = LearningResource.objects.all()
    serializer_class = LearningResourceSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ('subject', 'resource_type', 'difficulty_level')
    search_fields = ('title', 'provider')


class LearningPathViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PersonalizedLearningPath.objects.all()
    serializer_class = PersonalizedLearningPathSerializer
    filterset_fields = ('student', 'subject')


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [ReadOnlyOrTeacher]


class StudentBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentBadge.objects.all()
    serializer_class = StudentBadgeSerializer
    filterset_fields = ('student', 'badge')


class StudentPointViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentPoint.objects.all()
    serializer_class = StudentPointSerializer
    filterset_fields = ('student', 'category')


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('start_datetime')
    serializer_class = EventSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ('event_type', 'related_course', 'related_subject')


class ParentTeacherMeetingViewSet(viewsets.ModelViewSet):
    queryset = ParentTeacherMeeting.objects.all().order_by('-meeting_date')
    serializer_class = ParentTeacherMeetingSerializer
    filterset_fields = ('parent', 'teacher', 'student', 'status')


class ProgressReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgressReport.objects.all().order_by('-report_date')
    serializer_class = ProgressReportSerializer
    filterset_fields = ('student', 'report_type')


# --- identity + role dashboards ---------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_api(request):
    """Current user + role. The frontend calls this after login to route by role."""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_api(request):
    """Dashboard payload for the logged-in student (or a ?student=<id> for staff)."""
    student_id = request.query_params.get('student')
    if student_id:
        student = Student.objects.filter(pk=student_id).first()
    else:
        student = Student.objects.filter(user=request.user).first()
    if not student:
        return Response({'error': 'No student record for this user.'},
                        status=status.HTTP_404_NOT_FOUND)

    results = list(Result.objects.filter(student=student).select_related('exam'))
    upcoming = Exam.objects.filter(
        date__gte=timezone.now().date()).order_by('date')[:5]
    trend = results[-8:]
    subject_avg = (Result.objects.filter(student=student)
                   .values('exam__subject__name')
                   .annotate(avg=Avg('marks_obtained')))
    present = AttendanceRecord.objects.filter(student=student, status='present').count()

    return Response({
        'student': StudentSerializer(student).data,
        'attendance': student.attendance,
        'marks': student.marks,
        'cgpa': student.cgpa,
        'present': present,
        'enrollments_count': StudentEnrollment.objects.filter(student=student).count(),
        'results': ResultSerializer(results, many=True).data,
        'upcoming_exams': ExamSerializer(upcoming, many=True).data,
        'badges': StudentBadgeSerializer(
            StudentBadge.objects.filter(student=student), many=True).data,
        'points_total': sum(p.points for p in StudentPoint.objects.filter(student=student)),
        'predictions': PredictionResultSerializer(
            PredictionResult.objects.filter(student=student), many=True).data,
        'progress_reports': ProgressReportSerializer(
            ProgressReport.objects.filter(student=student)[:5], many=True).data,
        'charts': {
            'trend_labels': [r.exam.name for r in trend],
            'trend_values': [r.marks_obtained for r in trend],
            'subject_labels': [s['exam__subject__name'] for s in subject_avg],
            'subject_values': [round(s['avg'] or 0, 1) for s in subject_avg],
        },
    })


@api_view(['GET'])
@permission_classes([IsTeacherOrAdmin])
def teacher_dashboard_api(request):
    """Dashboard payload for a teacher: their courses + at-risk students."""
    courses = Course.objects.filter(teacher=request.user)
    at_risk = PredictionResult.objects.filter(
        risk_level__in=['high', 'medium']).select_related('student')[:20]
    return Response({
        'courses': CourseSerializer(courses, many=True).data,
        'total_students': Student.objects.filter(status='active').count(),
        'at_risk': PredictionResultSerializer(at_risk, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parent_dashboard_api(request):
    """Dashboard payload for a parent: their linked children + summaries."""
    parent = Parent.objects.filter(user=request.user).first()
    if not parent:
        return Response({'error': 'No parent record for this user.'},
                        status=status.HTTP_404_NOT_FOUND)
    children = [link.student for link in
                ParentStudentLink.objects.filter(parent=parent).select_related('student')]
    return Response({
        'parent': ParentSerializer(parent).data,
        'children': StudentSerializer(children, many=True).data,
        'meetings': ParentTeacherMeetingSerializer(
            ParentTeacherMeeting.objects.filter(parent=parent), many=True).data,
        'progress_reports': ProgressReportSerializer(
            ProgressReport.objects.filter(student__in=children), many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard_api(request):
    """API endpoint for admin dashboard data."""
    total_students = Student.objects.filter(status='active').count()
    total_teachers = UserProfile.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    avg_attendance = Student.objects.filter(status='active').aggregate(
        avg=Avg('attendance'))['avg'] or 0
    avg_marks = Student.objects.filter(status='active').aggregate(
        avg=Avg('marks'))['avg'] or 0

    # Attendance distribution buckets (matches the doughnut in admin_dashboard.html).
    active = Student.objects.filter(status='active')
    att_buckets = [
        ('<60%', active.filter(attendance__lt=60).count()),
        ('60-75%', active.filter(attendance__gte=60, attendance__lt=75).count()),
        ('75-90%', active.filter(attendance__gte=75, attendance__lt=90).count()),
        ('90%+', active.filter(attendance__gte=90).count()),
    ]
    grade_dist = (Result.objects.values('grade')
                  .annotate(n=Count('id')).order_by('grade'))
    subject_perf = (Result.objects.values('exam__subject__name')
                    .annotate(avg=Avg('marks_obtained')))

    at_risk = PredictionResult.objects.filter(
        risk_level__in=['high', 'medium']).select_related('student')[:10]
    recent = Result.objects.select_related('student', 'exam').order_by('-id')[:10]
    ratings = Feedback.objects.aggregate(avg=Avg('rating'))

    return Response({
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'avg_attendance': round(avg_attendance, 1),
        'avg_marks': round(avg_marks, 1),
        'avg_rating': round(ratings['avg'] or 0, 1),
        'total_feedback': Feedback.objects.count(),
        'at_risk_students': PredictionResultSerializer(at_risk, many=True).data,
        'recent_results': ResultSerializer(recent, many=True).data,
        'charts': {
            'attendance_labels': [b[0] for b in att_buckets],
            'attendance_values': [b[1] for b in att_buckets],
            'grade_labels': [g['grade'] or '—' for g in grade_dist],
            'grade_values': [g['n'] for g in grade_dist],
            'subject_labels': [s['exam__subject__name'] for s in subject_perf],
            'subject_values': [round(s['avg'] or 0, 1) for s in subject_perf],
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_api(request):
    """Global search API endpoint."""
    query = request.query_params.get('q', '')

    if not query:
        return Response({'error': 'Query parameter q is required'}, status=status.HTTP_400_BAD_REQUEST)

    students = Student.objects.filter(name__icontains=query)[:10]
    courses = Course.objects.filter(name__icontains=query)[:10]
    subjects = Subject.objects.filter(name__icontains=query)[:10]

    return Response({
        'students': StudentSerializer(students, many=True).data,
        'courses': CourseSerializer(courses, many=True).data,
        'subjects': SubjectSerializer(subjects, many=True).data,
    })
