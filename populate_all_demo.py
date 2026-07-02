
import os
import django
from datetime import datetime, timedelta
from random import randint, sample, choice as _rand_choice

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()


# Helper to support choice(..., k=...)
def choice(lst, k=None):
    from random import sample, choice as _rand_choice
    if k is None:
        return _rand_choice(lst)
    # if requesting more or equal to list size, return full list
    if k >= len(lst):
        return list(lst)
    return sample(lst, k)

from django.contrib.auth.models import User
from students.models import Student, Subject, Course, StudentEnrollment, Exam, Result, AttendanceRecord
from accounts.models import UserProfile
from advanced_features.models import (
    Parent, ParentStudentLink,
    GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath,
    Badge, StudentBadge, StudentPoint,
    Event, EventAttendee,
    ParentTeacherMeeting, ProgressReport
)


def create_demo_accounts_and_academics():
    """Create demo users (admin, teacher, students, parent) and minimal academic records if missing.
    This ensures the demo population script can run even on a fresh database.
    """
    # Demo users
    admin_user, _ = User.objects.get_or_create(username='admin_demo', defaults={'email': 'admin@example.com'})
    admin_user.set_password('admin1234')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

    teacher_user, _ = User.objects.get_or_create(username='teacher_demo', defaults={'email': 'teacher@example.com'})
    teacher_user.set_password('teacher1234')
    teacher_user.is_staff = True
    teacher_user.save()
    UserProfile.objects.get_or_create(user=teacher_user, defaults={'role': 'teacher'})

    # Create 2 demo students with linked user accounts
    students_created = []
    for i in range(1, 4):
        uname = f'student_demo{i}'
        u, _ = User.objects.get_or_create(username=uname, defaults={'email': f'{uname}@example.com'})
        u.set_password('student1234')
        u.save()
        UserProfile.objects.get_or_create(user=u, defaults={'role': 'student'})

        # Create Student record if not exists
        student_obj, created = Student.objects.get_or_create(
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
            }
        )
        students_created.append(student_obj)

    # Parent demo
    parent_user, _ = User.objects.get_or_create(username='parent_demo', defaults={'email': 'parent@example.com'})
    parent_user.set_password('parent1234')
    parent_user.save()
    UserProfile.objects.get_or_create(user=parent_user, defaults={'role': 'parent'})

    # Create Parent record and link to first student
    from advanced_features.models import Parent, ParentStudentLink
    parent_obj, _ = Parent.objects.get_or_create(user=parent_user, defaults={'name': 'Demo Parent', 'phone': '123-456-7890', 'email': 'parent@example.com'})
    if students_created:
        ParentStudentLink.objects.get_or_create(parent=parent_obj, student=students_created[0])

    # Ensure minimal academic records exist (Department, Course, Subject)
    from students.models import Department, AcademicYear, Semester, Course
    dept, _ = Department.objects.get_or_create(code='CE', defaults={'name': 'Computer Engineering', 'description': 'Engineering faculty - Computer/Systems'})
    year_name = '2026-2027'
    acad_year, _ = AcademicYear.objects.get_or_create(name=year_name, defaults={'start_date': datetime(2026, 7, 1).date(), 'end_date': datetime(2027, 6, 30).date(), 'active': True})
    sem, _ = Semester.objects.get_or_create(name='Fall 2026', defaults={'semester_type': 'fall', 'academic_year': acad_year, 'start_date': datetime(2026, 7, 1).date(), 'end_date': datetime(2026, 12, 31).date(), 'active': True})
    course, _ = Course.objects.get_or_create(code='CE101', defaults={'name': 'Data Structures', 'description': 'Intro to data structures', 'teacher': teacher_user, 'department': dept, 'academic_year': acad_year, 'semester': sem})
    Subject.objects.get_or_create(code='CE101-DS', course=course, defaults={'name': 'Data Structures', 'description': 'Arrays, lists, trees', 'department': dept})



def populate_all():
    print("=== Populating All Demo Data ===\n")

    # Ensure demo accounts and basic academic data exist
    try:
        create_demo_accounts_and_academics()
    except Exception:
        # If something goes wrong here, continue so existing data can still be populated
        pass

    # Get existing students and subjects
    students = list(Student.objects.all())
    subjects = list(Subject.objects.all())
    teachers = list(User.objects.filter(profile__role='teacher'))

    if not students:
        print("No students found! Please ensure demo data exists.")
        return

    if not subjects:
        print("No subjects found! Please ensure demo data exists.")
        return

    # --- Enroll students in teacher courses and create minimal exams/results/attendance ---
    teacher_courses = list(Course.objects.filter(teacher__in=teachers))
    if teacher_courses:
        for student in students:
            for c in teacher_courses:
                StudentEnrollment.objects.get_or_create(student=student, course=c, defaults={'status': 'enrolled'})

        # Create an exam and results/attendance for each subject in teacher courses
        for course_obj in teacher_courses:
            for subj in course_obj.subjects.all():
                exam_date = datetime.now().date() + timedelta(days=14)
                exam, _ = Exam.objects.get_or_create(
                    name=f"{subj.name} Midterm",
                    subject=subj,
                    defaults={'total_marks': 100, 'date': exam_date, 'exam_type': 'midterm'}
                )
                enrollments = StudentEnrollment.objects.filter(course=course_obj, status='enrolled')
                for enroll in enrollments:
                    # create a result if missing
                    Result.objects.get_or_create(
                        student=enroll.student,
                        exam=exam,
                        defaults={'marks_obtained': randint(45, 90)}
                    )
                    # add some attendance records
                    for d in range(5):
                        att_date = datetime.now().date() - timedelta(days=d)
                        AttendanceRecord.objects.get_or_create(
                            student=enroll.student,
                            subject=subj,
                            date=att_date,
                            defaults={'status': choice(['present', 'absent', 'late'])}
                        )
        print("  Enrollments, exams, results, and attendance created for teacher courses.\n")

    # --- 1. Badges ---
    print("Creating badges...")
    badges_data = [
        ("Perfect Attendance", "100% attendance for a week", "attendance", "bi-calendar-check"),
        ("Top Performer", "90%+ marks in a subject", "performance", "bi-trophy"),
        ("Most Improved", "15% improvement in marks", "improvement", "bi-arrow-up-circle"),
        ("Active Participant", "Active in class activities", "participation", "bi-star"),
        ("Quiz Champion", "Won 3 quizzes", "performance", "bi-award"),
    ]


    badge_objs = []
    for name, desc, b_type, icon in badges_data:
        badge, _ = Badge.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'badge_type': b_type, 'icon': icon, 'points_required': 0}
        )
        badge_objs.append(badge)
    print(f"  {len(badge_objs)} badges created/updated.\n")

    # --- 2. Student Points and Badges ---
    print("Creating student points and badges...")
    point_reasons = [
        "Attended full week", "Good performance in quiz", "Class participation",
        "Submitted assignment early", "Helped a classmate", "Good behavior"
    ]
    for student in students:
        # Add points
        for _ in range(randint(5, 15)):
            StudentPoint.objects.create(
                student=student,
                points=randint(5, 25),
                reason=choice(point_reasons),
                category=choice(['attendance', 'marks', 'participation', 'other'])
            )
        # Add badges
        num_badges = randint(1, 3)
        selected_badges = choice(badge_objs, k=num_badges) if len(badge_objs) > num_badges else badge_objs
        for b in selected_badges:
            StudentBadge.objects.get_or_create(student=student, badge=b)
    print("  Points and badges added for all students.\n")

    # --- 3. Academic Forecasts and WhatIf Scenarios ---
    print("Creating academic forecasts and what-if scenarios...")
    for student in students:
        for subject in subjects:
            # Forecast
            predicted_marks = max(30, min(100, student.marks + randint(-10, 15)))
            confidence = randint(70, 95)
            GradeForecast.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    'predicted_marks': predicted_marks,
                    'confidence_score': confidence,
                    'remarks': "Mid-semester forecast based on current performance"
                }
            )

            # WhatIf
            WhatIfScenario.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    'attendance_change_pct': 10,
                    'marks_change_pct': 8,
                    'predicted_new_marks': min(100, predicted_marks + 8)
                }
            )
    print("  Academic forecasts and what-if scenarios created.\n")

    # --- 4. Learning Resources ---
    print("Creating learning resources...")
    resources_data = []
    for subject in subjects:
        resources_data.extend([
            (f"{subject.name} Basics", "video", f"https://www.khanacademy.org/search?page_search_query={subject.name.lower().replace(' ', '+')}", 2, "Khan Academy"),
            (f"{subject.name} Practice Problems", "practice", f"https://www.khanacademy.org/search?page_search_query={subject.name.lower().replace(' ', '+')}+practice", 3, "Khan Academy"),
            (f"{subject.name} Full Course", "course", f"https://www.coursera.org/search?query={subject.name.lower().replace(' ', '+')}", 4, "Coursera"),
            (f"{subject.name} Quick Guide", "article", f"https://en.wikipedia.org/wiki/{subject.name.replace(' ', '_')}", 1, "Wikipedia"),
        ])
    resource_objs = []
    for title, r_type, url, diff, provider in resources_data:
        # Find subject (first subject matching name start)
        subj = next((s for s in subjects if s.name.lower() in title.lower()), subjects[0])
        resource, _ = LearningResource.objects.get_or_create(
            title=title,
            subject=subj,
            defaults={'description': f"Learn {title} with {provider}", 'resource_type': r_type, 'url': url, 'difficulty_level': diff, 'provider': provider}
        )
        resource_objs.append(resource)
    print(f"  {len(resource_objs)} learning resources created/updated.\n")

    # --- 5. Personalized Learning Paths ---
    print("Creating personalized learning paths...")
    weak_topics_list = [
        "Quadratic equations, Probability",
        "Newton's laws, Thermodynamics",
        "Organic chemistry, Periodic table",
        "World War II, Ancient civilizations",
        "Grammar, Essay writing",
    ]
    for student in students:
        for subject in subjects:
            lp, created = PersonalizedLearningPath.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={
                    'weak_topics': choice(weak_topics_list),
                    'recommended_study_hours': randint(3, 7)
                }
            )
            if created:
                # Add 2-3 resources
                subj_resources = [r for r in resource_objs if r.subject == subject]
                if subj_resources:
                    num_res = min(randint(2,3), len(subj_resources))
                    lp.resources.add(*choice(subj_resources, k=num_res))
    print("  Personalized learning paths created.\n")

    # --- 6. Events ---
    print("Creating calendar events...")
    event_types = ['class', 'exam', 'meeting', 'assignment']
    event_titles = [
        "Engineering Seminar", "Systems Exam", "Advising Meeting", "Design Assignment",
        "Chemistry Lab", "Engineering Quiz", "Biology Class", "Computer Science Project"
    ]
    now = datetime.now()
    for i in range(8):
        start = now + timedelta(days=i, hours=9 + randint(0,3))
        end = start + timedelta(hours=1)
        event = Event.objects.create(
            title=f"{choice(event_titles)} #{i+1}",
            description=f"{'Class, exam, meeting, or assignment'}. Don't forget!",
            event_type=choice(event_types),
            start_datetime=start,
            end_datetime=end,
            location=choice(["Engineering Hall 101", "Lab 202", "Online (Zoom)", "Room 303"]),
            related_subject=choice(subjects) if subjects else None,
            related_course=(subjects[0].course if subjects and getattr(subjects[0], 'course', None) else None),
            created_by=teachers[0] if teachers else None
        )
        # Add attendees
        for s in students[:5]:
            if s.user:
                EventAttendee.objects.get_or_create(event=event, user=s.user)
    print("  8 events created with attendees.\n")

    # --- 7. Progress Reports ---
    print("Creating progress reports...")
    for student in students:
        for report_type in ['weekly', 'monthly']:
            ProgressReport.objects.get_or_create(
                student=student,
                report_type=report_type,
                report_date=now.date(),
                defaults={
                    'attendance_pct': student.attendance,
                    'avg_marks': student.marks,
                    'weak_subjects': choice([s.name for s in subjects]),
                    'strong_subjects': choice([s.name for s in subjects]),
                    'teacher_comments': "Strong technical progress. Continue refining your design skills.",
                    'is_sent': True
                }
            )
    print("  Weekly and monthly progress reports created for all students.\n")

    # --- 8. Advising Meetings ---
    if teachers and Parent.objects.exists() and students:
        print("Creating advising meetings...")
        parent = Parent.objects.first()
        student = ParentStudentLink.objects.filter(parent=parent).first().student if ParentStudentLink.objects.exists() else students[0]
        for i in range(2):
            meeting_date = now + timedelta(days=10 + i*14)
            ParentTeacherMeeting.objects.get_or_create(
                parent=parent,
                teacher=teachers[0],
                student=student,
                meeting_date=meeting_date,
                defaults={
                    'meeting_link': "https://zoom.us/j/1234567890",
                    'location': "Engineering Building 404",
                    'agenda': "Discuss mid-semester performance and improvement areas",
                    'status': 'scheduled'
                }
            )
        print("  2 advising meetings scheduled.\n")

    print("=== Done! All demo data populated successfully! ===")


if __name__ == "__main__":
    # Fix random choice to work with lists
    populate_all()
