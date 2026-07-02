from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserProfile
from students.models import (
    AttendanceRecord,
    Course,
    Exam,
    Feedback,
    Result,
    Student,
    Subject,
)


class StudentScopedViewsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.teacher_user = self.user_model.objects.create_user(username='teacher1', password='testpass123')
        UserProfile.objects.create(user=self.teacher_user, role='teacher')

        self.student_user = self.user_model.objects.create_user(username='student_viewer', password='testpass123')
        UserProfile.objects.create(user=self.student_user, role='student')
        self.student = Student.objects.create(user=self.student_user, name='Viewer Student')

        self.other_user = self.user_model.objects.create_user(username='student_other', password='testpass123')
        UserProfile.objects.create(user=self.other_user, role='student')
        self.other_student = Student.objects.create(user=self.other_user, name='Other Student')

        self.course = Course.objects.create(name='Math', code='MATH101', teacher=self.teacher_user)
        self.subject = Subject.objects.create(name='Algebra', code='ALG101', course=self.course)
        self.exam = Exam.objects.create(name='Midterm', subject=self.subject, total_marks=100, date='2026-06-25')
        self.student.enrollments.create(course=self.course, status='enrolled')

        Result.objects.create(student=self.student, exam=self.exam, marks_obtained=80)
        Result.objects.create(student=self.other_student, exam=self.exam, marks_obtained=60)

        AttendanceRecord.objects.create(student=self.student, subject=self.subject, date='2026-06-24', status='present')
        AttendanceRecord.objects.create(student=self.other_student, subject=self.subject, date='2026-06-24', status='absent')

        Feedback.objects.create(student=self.student, teacher=self.teacher_user, rating=5, comment='Great work')
        Feedback.objects.create(student=self.other_student, teacher=self.teacher_user, rating=2, comment='Needs work')

    def test_student_sees_only_their_own_data(self):
        self.client.force_login(self.student_user)

        exam_response = self.client.get('/exams/')
        result_response = self.client.get('/results/')
        attendance_response = self.client.get('/attendance/')
        feedback_response = self.client.get('/feedback/')

        self.assertEqual(exam_response.status_code, 200)
        self.assertEqual(result_response.status_code, 200)
        self.assertEqual(attendance_response.status_code, 200)
        self.assertEqual(feedback_response.status_code, 200)

        self.assertEqual(list(exam_response.context['exams'].values_list('id', flat=True)), [self.exam.id])
        self.assertEqual(list(result_response.context['results'].values_list('student__id', flat=True)), [self.student.id])
        self.assertEqual(list(attendance_response.context['records'].values_list('student__id', flat=True)), [self.student.id])
        self.assertEqual(list(feedback_response.context['feedbacks'].values_list('student__id', flat=True)), [self.student.id])
