
import os
import django
from datetime import datetime, timedelta
from random import randint, choice

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()

from students.models import Student, Subject
from accounts.models import UserProfile
from advanced_features.models import (
    Parent, ParentStudentLink,
    GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath,
    Badge, StudentBadge, StudentPoint,
    Event, EventAttendee,
    ParentTeacherMeeting, ProgressReport
)


def create_parent():
    print("Creating demo parent...")

    # Create parent user
    user, created = User.objects.get_or_create(username='parent_demo')
    if created:
        user.set_password('parent1234')
        user.save()

    # Create profile
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'parent'})

    # Create Parent record
    parent, _ = Parent.objects.get_or_create(user=user, defaults={'name': 'John Parent', 'phone': '123-456-7890', 'email': 'parent@example.com'})

    # Link to first student
    student = Student.objects.first()
    if student:
        ParentStudentLink.objects.get_or_create(parent=parent, student=student)
        print(f"Linked parent to student: {student.name}")

    # Create badges
    print("\nCreating badges...")
    badges = [
        {'name': 'Perfect Attendance', 'description': '100% attendance', 'badge_type': 'attendance', 'icon': 'bi-calendar-check', 'points_required': 0},
        {'name': 'Top Performer', 'description': '90%+ marks', 'badge_type': 'performance', 'icon': 'bi-trophy', 'points_required': 0},
        {'name': 'Most Improved', 'description': '15% improvement', 'badge_type': 'improvement', 'icon': 'bi-arrow-up-circle', 'points_required': 0},
        {'name': 'Active Participant', 'description': 'Active in class', 'badge_type': 'participation', 'icon': 'bi-star', 'points_required': 0}
    ]
    for b_data in badges:
        Badge.objects.get_or_create(name=b_data['name'], defaults=b_data)

    # Give some points to students
    print("\nCreating student points and badges...")
    students = Student.objects.all()
    badge_objs = Badge.objects.all()
    for s in students:
        # Points
        for _ in range(randint(3, 10)):
            StudentPoint.objects.create(
                student=s,
                points=randint(5, 20),
                reason=choice(['Attended class', 'Good performance', 'Participation', 'Assignment submitted']),
                category=choice(['attendance', 'marks', 'participation', 'other'])
            )
        # Badges
        badge_objs_list = list(badge_objs)
        for _ in range(randint(1, 3)):
            b = choice(badge_objs_list)
            StudentBadge.objects.get_or_create(student=s, badge=b)

    # Create academic forecasts
    print("\nCreating academic forecasts...")
    subjects = Subject.objects.all()
    for s in students:
        for subj in subjects:
            GradeForecast.objects.get_or_create(
                student=s,
                subject=subj,
                defaults={'predicted_marks': round(s.marks + randint(-10, 10)), 'confidence_score': 80 + randint(0, 19), 'remarks': 'Mid-semester prediction'}
            )
            WhatIfScenario.objects.get_or_create(
                student=s,
                subject=subj,
                defaults={'attendance_change_pct': 10, 'marks_change_pct': 5, 'predicted_new_marks': s.marks + 5}
            )

    # Create learning resources
    print("\nCreating learning resources...")
    if subjects.exists():
        subj = subjects.first()
        resources = [
            {'title': 'Algebra Basics', 'resource_type': 'video', 'url': 'https://example.com/algebra', 'difficulty_level': 3, 'provider': 'Khan Academy'},
            {'title': 'Calculus Practice', 'resource_type': 'practice', 'url': 'https://example.com/calculus', 'difficulty_level': 4, 'provider': 'Coursera'},
            {'title': 'Physics Concepts', 'resource_type': 'article', 'url': 'https://example.com/physics', 'difficulty_level': 2, 'provider': 'MIT OpenCourseWare'}
        ]
        for r_data in resources:
            LearningResource.objects.get_or_create(title=r_data['title'], subject=subj, defaults=r_data)

    # Create learning paths
    print("\nCreating personalized learning paths...")
    res = LearningResource.objects.all()
    for s in students:
        for subj in subjects:
            lp, created = PersonalizedLearningPath.objects.get_or_create(
                student=s,
                subject=subj,
                defaults={'weak_topics': 'Quadratic equations, Probability', 'recommended_study_hours': 5}
            )
            if created and res.exists():
                lp.resources.add(*list(res)[:2])

    # Create events
    print("\nCreating events...")
    teachers = User.objects.filter(profile__role='teacher')
    now = datetime.now()
    for i in range(3):
        event = Event.objects.create(
            title=f"{choice(['Engineering Seminar', 'Systems Exam', 'Advising Meeting', 'Lab Assignment'])} {i+1}",
            description=f"Event description {i+1}",
            event_type=choice(['class', 'exam', 'meeting', 'assignment']),
            start_datetime=now + timedelta(days=i+1, hours=10),
            end_datetime=now + timedelta(days=i+1, hours=12),
            location=choice(['Engineering Hall 101', 'Lab 202', 'Online']),
            created_by=teachers.first() if teachers.exists() else None
        )
        for s in students[:3]:
            if s.user:
                EventAttendee.objects.get_or_create(event=event, user=s.user, defaults={'is_attending': True})

    # Create progress reports
    print("\nCreating progress reports...")
    for s in students:
        ProgressReport.objects.get_or_create(
            student=s,
            report_type=choice(['weekly', 'monthly']),
            report_date=now.date(),
            defaults={'attendance_pct': s.attendance, 'avg_marks': s.marks, 'weak_topics': 'Circuits', 'strong_topics': 'Thermodynamics', 'teacher_comments': 'Strong technical progress. Continue refining your design skills.', 'is_sent': True}
        )

    # Create advising meetings
    print("\nCreating advising meetings...")
    if student and parent and teachers.exists():
        ParentTeacherMeeting.objects.get_or_create(
            parent=parent,
            teacher=teachers.first(),
            student=student,
            meeting_date=now + timedelta(days=7),
            meeting_link='https://meet.google.com/abc-def-ghi',
            agenda='Discuss mid-semester progress',
            status='scheduled'
        )

    print("\nDone! Demo data for advanced features created!")


if __name__ == "__main__":
    create_parent()
