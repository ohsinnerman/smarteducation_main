"""
`python manage.py seed_demo_data`

Single canonical, idempotent seed path. Consolidates the old root-level
populate_all_demo.py / populate_demo_advanced.py / fix_parent.py scripts:
creates demo login accounts, academic records (departments/courses/subjects/
exams/results/attendance), and advanced-feature demo data (badges, points,
forecasts, resources, learning paths, events, progress reports, PTMs).

Idempotent: safe to re-run. Prints a summary at the end.
"""

from datetime import datetime, timedelta
from random import randint, sample, choice as _rand_choice

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile
from students.models import (
    Student, Subject, Course, StudentEnrollment, Exam, Result,
    AttendanceRecord, Department, AcademicYear, Semester,
)
from advanced_features.models import (
    Parent, ParentStudentLink, GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath, Badge, StudentBadge,
    StudentPoint, Event, EventAttendee, ParentTeacherMeeting, ProgressReport,
)


def choice(lst, k=None):
    if k is None:
        return _rand_choice(lst)
    if k >= len(lst):
        return list(lst)
    return sample(lst, k)


class Command(BaseCommand):
    help = "Seed the database with a full, idempotent demo dataset."

    def handle(self, *args, **options):
        self._seed_accounts_and_academics()
        self._seed_extra_depth()
        self._seed_advanced()
        self._summary()

    # ------------------------------------------------------------------ #
    def _seed_extra_depth(self):
        """Bulk, diverse, legit-looking academic data. Keeps the 6 login users
        but adds many more (unlinked) student records, departments, courses,
        subjects, exams, results, attendance and feedback so dashboards look real.
        """
        self.stdout.write("Seeding extended demo depth (diverse data)…")
        teacher = User.objects.filter(profile__role='teacher').first()

        # Departments + subjects across several disciplines.
        dept_specs = [
            ('CE', 'Computer Engineering', ['Data Structures', 'Operating Systems', 'Databases', 'Machine Learning']),
            ('EE', 'Electrical Engineering', ['Circuit Theory', 'Signals & Systems', 'Power Electronics']),
            ('ME', 'Mechanical Engineering', ['Thermodynamics', 'Fluid Mechanics', 'Robotics']),
            ('MA', 'Mathematics', ['Linear Algebra', 'Calculus III', 'Probability']),
            ('PH', 'Physics', ['Quantum Mechanics', 'Electromagnetism']),
        ]
        acad_year = AcademicYear.objects.first()
        sem = Semester.objects.first()
        all_subjects = []
        for code, name, subjects in dept_specs:
            dept, _ = Department.objects.get_or_create(
                code=code, defaults={'name': name, 'description': f'{name} faculty'})
            course, _ = Course.objects.get_or_create(
                code=f'{code}101',
                defaults={'name': f'{name} Core', 'description': f'Core {name} course',
                          'teacher': teacher, 'department': dept,
                          'academic_year': acad_year, 'semester': sem})
            for i, sname in enumerate(subjects):
                subj, _ = Subject.objects.get_or_create(
                    code=f'{code}-{i}', course=course,
                    defaults={'name': sname, 'description': sname, 'department': dept})
                all_subjects.append(subj)

        # A diverse roster of students (names, programs, years, performance spread).
        first = ['Aarav', 'Diya', 'Vivaan', 'Ananya', 'Aditya', 'Ishita', 'Kabir', 'Sara',
                 'Reyansh', 'Myra', 'Arjun', 'Anika', 'Vihaan', 'Riya', 'Ayaan', 'Kiara',
                 'Rohan', 'Meera', 'Dev', 'Tara', 'Karan', 'Nisha', 'Yash', 'Pooja',
                 'Aryan', 'Sneha', 'Ved', 'Isha', 'Neil', 'Zara']
        last = ['Sharma', 'Patel', 'Reddy', 'Nair', 'Iyer', 'Gupta', 'Singh', 'Rao',
                'Mehta', 'Bose', 'Khan', 'Das', 'Joshi', 'Menon', 'Kapoor']
        programs = ['btech', 'bsc', 'mtech', 'msc', 'ba', 'bcom']
        specs = ['Computer Science', 'Electronics', 'Mechanical', 'Applied Math',
                 'Physics', 'Data Science', 'Robotics']

        students = list(Student.objects.all())
        target = 33  # total students incl. the 3 demo-linked ones
        for i in range(len(students), target):
            fn = _rand_choice(first)
            ln = _rand_choice(last)
            # Performance archetype: mix of strong / average / struggling.
            band = _rand_choice(['strong', 'strong', 'avg', 'avg', 'avg', 'weak'])
            if band == 'strong':
                att, mk, cg = randint(88, 99), randint(78, 96), round(randint(80, 95) / 10, 2)
            elif band == 'avg':
                att, mk, cg = randint(72, 88), randint(58, 78), round(randint(60, 80) / 10, 2)
            else:
                att, mk, cg = randint(45, 70), randint(28, 55), round(randint(35, 58) / 10, 2)
            Student.objects.get_or_create(
                roll_number=f'2026{_rand_choice(["CE", "EE", "ME", "MA", "PH"])}{100 + i}',
                defaults={
                    'name': f'{fn} {ln}',
                    'program': _rand_choice(programs),
                    'year': randint(1, 4),
                    'specialization': _rand_choice(specs),
                    'status': _rand_choice(['active', 'active', 'active', 'graduated']),
                    'attendance': att, 'marks': mk, 'cgpa': cg,
                })

        students = list(Student.objects.all())

        # Exams across subjects + results for a random sample of students.
        exam_types = ['midterm', 'final', 'quiz', 'assignment', 'lab', 'presentation']
        for subj in all_subjects:
            for et in _rand_choice([exam_types, exam_types[:3], exam_types[2:]]):
                exam, _ = Exam.objects.get_or_create(
                    name=f'{subj.name} {et.title()}', subject=subj,
                    defaults={'total_marks': 100,
                              'date': datetime.now().date() + timedelta(days=randint(-30, 40)),
                              'exam_type': et})
                for student in sample(students, k=min(len(students), randint(12, 22))):
                    base = student.marks + randint(-12, 12)
                    Result.objects.get_or_create(
                        student=student, exam=exam,
                        defaults={'marks_obtained': max(10, min(100, base))})

        # Attendance spread over the last few weeks.
        for student in students:
            for subj in sample(all_subjects, k=min(len(all_subjects), 4)):
                for d in range(0, randint(6, 12)):
                    AttendanceRecord.objects.get_or_create(
                        student=student, subject=subj,
                        date=datetime.now().date() - timedelta(days=d),
                        defaults={'status': _rand_choice(
                            ['present', 'present', 'present', 'late', 'absent'])})

        # Feedback so the admin rating tile is non-trivial.
        from students.models import Feedback
        comments = ['Very engaged in class.', 'Needs to submit work on time.',
                    'Excellent problem solver.', 'Improving steadily.',
                    'Great teamwork.', 'Should ask more questions.']
        for student in sample(students, k=min(len(students), 20)):
            Feedback.objects.get_or_create(
                student=student, teacher=teacher,
                defaults={'rating': randint(3, 5), 'comment': _rand_choice(comments)})

    # ------------------------------------------------------------------ #
    def _seed_accounts_and_academics(self):
        self.stdout.write("Seeding demo accounts and academic records…")

        admin_user, _ = User.objects.get_or_create(
            username='admin_demo', defaults={'email': 'admin@example.com'})
        admin_user.set_password('admin1234')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

        teacher_user, _ = User.objects.get_or_create(
            username='teacher_demo', defaults={'email': 'teacher@example.com'})
        teacher_user.set_password('teacher1234')
        teacher_user.is_staff = True
        teacher_user.save()
        UserProfile.objects.get_or_create(user=teacher_user, defaults={'role': 'teacher'})

        students_created = []
        for i in range(1, 4):
            uname = f'student_demo{i}'
            u, _ = User.objects.get_or_create(
                username=uname, defaults={'email': f'{uname}@example.com'})
            u.set_password('student1234')
            u.save()
            UserProfile.objects.get_or_create(user=u, defaults={'role': 'student'})
            student_obj, _ = Student.objects.get_or_create(
                user=u,
                defaults={
                    'name': f'Demo Student {i}',
                    'roll_number': f'2026CE00{i}',
                    'program': 'btech',
                    'year': 2,
                    'specialization': 'Computer Engineering',
                    'attendance': 85 + i,
                    'marks': 65 + i * 5,
                    'cgpa': 7.5 + i * 0.1,
                },
            )
            students_created.append(student_obj)

        parent_user, _ = User.objects.get_or_create(
            username='parent_demo', defaults={'email': 'parent@example.com'})
        parent_user.set_password('parent1234')
        parent_user.save()
        UserProfile.objects.get_or_create(user=parent_user, defaults={'role': 'parent'})
        parent_obj, _ = Parent.objects.get_or_create(
            user=parent_user,
            defaults={'name': 'Demo Parent', 'phone': '123-456-7890',
                      'email': 'parent@example.com'})
        if students_created:
            ParentStudentLink.objects.get_or_create(
                parent=parent_obj, student=students_created[0])

        dept, _ = Department.objects.get_or_create(
            code='CE',
            defaults={'name': 'Computer Engineering',
                      'description': 'Engineering faculty - Computer/Systems'})
        acad_year, _ = AcademicYear.objects.get_or_create(
            name='2026-2027',
            defaults={'start_date': datetime(2026, 7, 1).date(),
                      'end_date': datetime(2027, 6, 30).date(), 'active': True})
        sem, _ = Semester.objects.get_or_create(
            name='Fall 2026',
            defaults={'semester_type': 'fall', 'academic_year': acad_year,
                      'start_date': datetime(2026, 7, 1).date(),
                      'end_date': datetime(2026, 12, 31).date(), 'active': True})
        course, _ = Course.objects.get_or_create(
            code='CE101',
            defaults={'name': 'Data Structures',
                      'description': 'Intro to data structures',
                      'teacher': teacher_user, 'department': dept,
                      'academic_year': acad_year, 'semester': sem})
        Subject.objects.get_or_create(
            code='CE101-DS', course=course,
            defaults={'name': 'Data Structures',
                      'description': 'Arrays, lists, trees', 'department': dept})

        # Enrollments, exams, results, attendance.
        students = list(Student.objects.all())
        teachers = list(User.objects.filter(profile__role='teacher'))
        for course_obj in Course.objects.filter(teacher__in=teachers):
            for student in students:
                StudentEnrollment.objects.get_or_create(
                    student=student, course=course_obj, defaults={'status': 'enrolled'})
            for subj in course_obj.subjects.all():
                exam, _ = Exam.objects.get_or_create(
                    name=f"{subj.name} Midterm", subject=subj,
                    defaults={'total_marks': 100,
                              'date': datetime.now().date() + timedelta(days=14),
                              'exam_type': 'midterm'})
                for enroll in StudentEnrollment.objects.filter(
                        course=course_obj, status='enrolled'):
                    Result.objects.get_or_create(
                        student=enroll.student, exam=exam,
                        defaults={'marks_obtained': randint(45, 90)})
                    for d in range(5):
                        AttendanceRecord.objects.get_or_create(
                            student=enroll.student, subject=subj,
                            date=datetime.now().date() - timedelta(days=d),
                            defaults={'status': choice(['present', 'absent', 'late'])})

    # ------------------------------------------------------------------ #
    def _seed_advanced(self):
        self.stdout.write("Seeding advanced-feature demo data…")
        students = list(Student.objects.all())
        subjects = list(Subject.objects.all())
        teachers = list(User.objects.filter(profile__role='teacher'))
        if not students or not subjects:
            self.stdout.write(self.style.WARNING(
                "  No students/subjects — skipping advanced seed."))
            return

        badge_objs = []
        for name, desc, b_type, icon in [
            ("Perfect Attendance", "100% attendance for a week", "attendance", "bi-calendar-check"),
            ("Top Performer", "90%+ marks in a subject", "performance", "bi-trophy"),
            ("Most Improved", "15% improvement in marks", "improvement", "bi-arrow-up-circle"),
            ("Active Participant", "Active in class activities", "participation", "bi-star"),
            ("Quiz Champion", "Won 3 quizzes", "performance", "bi-award"),
        ]:
            badge, _ = Badge.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'badge_type': b_type,
                          'icon': icon, 'points_required': 0})
            badge_objs.append(badge)

        reasons = ["Attended full week", "Good performance in quiz",
                   "Class participation", "Submitted assignment early",
                   "Helped a classmate", "Good behavior"]
        for student in students:
            if not StudentPoint.objects.filter(student=student).exists():
                for _ in range(randint(5, 15)):
                    StudentPoint.objects.create(
                        student=student, points=randint(5, 25),
                        reason=choice(reasons),
                        category=choice(['attendance', 'marks', 'participation', 'other']))
            for b in choice(badge_objs, k=randint(1, 3)):
                StudentBadge.objects.get_or_create(student=student, badge=b)

        for student in students:
            for subject in subjects:
                predicted = max(30, min(100, student.marks + randint(-10, 15)))
                GradeForecast.objects.get_or_create(
                    student=student, subject=subject,
                    defaults={'predicted_marks': predicted,
                              'confidence_score': randint(70, 95),
                              'remarks': "Mid-semester forecast"})
                WhatIfScenario.objects.get_or_create(
                    student=student, subject=subject,
                    defaults={'attendance_change_pct': 10, 'marks_change_pct': 8,
                              'predicted_new_marks': min(100, predicted + 8)})

        resource_objs = []
        for subject in subjects:
            q = subject.name.lower().replace(' ', '+')
            for title, r_type, url, diff, provider in [
                (f"{subject.name} Basics", "video", f"https://www.khanacademy.org/search?page_search_query={q}", 2, "Khan Academy"),
                (f"{subject.name} Practice", "practice", f"https://www.khanacademy.org/search?page_search_query={q}+practice", 3, "Khan Academy"),
                (f"{subject.name} Course", "course", f"https://www.coursera.org/search?query={q}", 4, "Coursera"),
            ]:
                r, _ = LearningResource.objects.get_or_create(
                    title=title, subject=subject,
                    defaults={'description': f"Learn {title} with {provider}",
                              'resource_type': r_type, 'url': url,
                              'difficulty_level': diff, 'provider': provider})
                resource_objs.append(r)

        for student in students:
            for subject in subjects:
                lp, created = PersonalizedLearningPath.objects.get_or_create(
                    student=student, subject=subject,
                    defaults={'weak_topics': "Core concepts",
                              'recommended_study_hours': randint(3, 7)})
                if created:
                    subj_res = [r for r in resource_objs if r.subject == subject]
                    if subj_res:
                        lp.resources.add(*choice(subj_res, k=min(2, len(subj_res))))

        now = datetime.now()
        if not Event.objects.exists():
            for i in range(8):
                start = now + timedelta(days=i, hours=9 + randint(0, 3))
                event = Event.objects.create(
                    title=f"Event #{i + 1}", description="Demo event.",
                    event_type=choice(['class', 'exam', 'meeting', 'assignment']),
                    start_datetime=start, end_datetime=start + timedelta(hours=1),
                    location=choice(["Hall 101", "Lab 202", "Online", "Room 303"]),
                    related_subject=choice(subjects),
                    created_by=teachers[0] if teachers else None)
                for s in students[:5]:
                    if s.user:
                        EventAttendee.objects.get_or_create(event=event, user=s.user)

        for student in students:
            for report_type in ['weekly', 'monthly']:
                ProgressReport.objects.get_or_create(
                    student=student, report_type=report_type, report_date=now.date(),
                    defaults={'attendance_pct': student.attendance,
                              'avg_marks': student.marks,
                              'weak_subjects': choice([s.name for s in subjects]),
                              'strong_subjects': choice([s.name for s in subjects]),
                              'teacher_comments': "Good progress.", 'is_sent': True})

        if teachers and Parent.objects.exists():
            parent = Parent.objects.first()
            link = ParentStudentLink.objects.filter(parent=parent).first()
            student = link.student if link else students[0]
            for i in range(2):
                ParentTeacherMeeting.objects.get_or_create(
                    parent=parent, teacher=teachers[0], student=student,
                    meeting_date=now + timedelta(days=10 + i * 14),
                    defaults={'meeting_link': "https://zoom.us/j/1234567890",
                              'location': "Building 404",
                              'agenda': "Discuss mid-semester performance",
                              'status': 'scheduled'})

    # ------------------------------------------------------------------ #
    def _summary(self):
        self.stdout.write(self.style.SUCCESS("\nSeed complete:"))
        for label, model in [
            ("Users", User), ("Students", Student), ("Courses", Course),
            ("Subjects", Subject), ("Exams", Exam), ("Results", Result),
            ("Attendance", AttendanceRecord), ("Badges", Badge),
            ("Events", Event), ("Progress reports", ProgressReport),
        ]:
            self.stdout.write(f"  {label:18} {model.objects.count()}")
        self.stdout.write("\nDemo logins: admin_demo/admin1234, teacher_demo/teacher1234, "
                          "student_demo1..3/student1234, parent_demo/parent1234")
