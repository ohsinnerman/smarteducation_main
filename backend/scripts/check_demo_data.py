import os
import sys
import pathlib
import django
# Ensure project root (parent of package) is on sys.path so settings import works
proj_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(proj_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Course, StudentEnrollment, Exam, Result, AttendanceRecord, Student
from advanced_features.models import Parent, ParentStudentLink

u = User.objects.filter(username='teacher_demo').first()
print('teacher_demo exists:', bool(u))
if u:
    courses = Course.objects.filter(teacher=u)
    print('courses count:', courses.count())
    for c in courses:
        print(f"Course {c.code} - {c.name}: enrollments={StudentEnrollment.objects.filter(course=c).count()}")
        for s in StudentEnrollment.objects.filter(course=c):
            student = s.student
            print('  student:', student.name, 'results:', Result.objects.filter(student=student, exam__subject__course=c).count(), 'attendance:', AttendanceRecord.objects.filter(student=student, subject__course=c).count())

p = User.objects.filter(username='parent_demo').first()
print('\nparent_demo exists:', bool(p))
if p:
    parent = Parent.objects.filter(user=p).first()
    if parent:
        linked = ParentStudentLink.objects.filter(parent=parent)
        print('linked students:', linked.count())
        for l in linked:
            print(' ', l.student.name)

# Print first 10 students visible to teacher_demo via enrollments
print('\nStudents visible to teacher_demo:')
if u:
    students = Student.objects.filter(enrollments__course__teacher=u).distinct()
    print('count:', students.count())
    for s in students:
        print(' -', s.name, s.program, s.year, 'attendance', s.attendance, 'marks', s.marks)

# Print courses visible to parent_demo
if p:
    if parent:
        courses_parent = Course.objects.filter(enrollments__student__in=[l.student for l in linked]).distinct()
        print('\nCourses visible to parent_demo:', courses_parent.count())
        for c in courses_parent:
            print(' -', c.code, c.name)
