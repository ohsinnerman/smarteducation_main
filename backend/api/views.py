from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Avg, Count

from students.models import Student, Course, Subject, Exam, Result, AttendanceRecord, StudentEnrollment, Feedback
from notifications.models import Notification, NotificationPreference
from ml.models import PredictionResult
from accounts.models import UserProfile

from .serializers import (
    UserSerializer, StudentSerializer, CourseSerializer, SubjectSerializer,
    ExamSerializer, ResultSerializer, AttendanceRecordSerializer,
    StudentEnrollmentSerializer, FeedbackSerializer, NotificationSerializer,
    NotificationPreferenceSerializer, PredictionResultSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filterset_fields = ('grade', 'section', 'status')
    search_fields = ('name',)


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
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ('student', 'exam', 'grade')
    search_fields = ('student__name',)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    filterset_fields = ('student', 'subject', 'status', 'date')
    search_fields = ('student__name',)


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    filterset_fields = ('student', 'course', 'status')


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):
    """API endpoint for admin dashboard data."""
    total_students = Student.objects.filter(status='active').count()
    total_teachers = UserProfile.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    avg_attendance = Student.objects.filter(status='active').aggregate(
        avg=Avg('attendance'))['avg'] or 0
    avg_marks = Student.objects.filter(status='active').aggregate(
        avg=Avg('marks'))['avg'] or 0

    return Response({
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'avg_attendance': round(avg_attendance, 1),
        'avg_marks': round(avg_marks, 1),
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
