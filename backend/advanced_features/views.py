
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from students.models import Student, Subject, Course
from accounts.models import UserProfile
from .models import (
    Parent, ParentStudentLink,
    GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath,
    Badge, StudentBadge, StudentPoint,
    Event, EventAttendee,
    ParentTeacherMeeting, ProgressReport
)


def is_admin(user):
    try:
        return user.profile.is_admin
    except:
        return False


def is_teacher(user):
    try:
        return user.profile.is_teacher
    except:
        return False


def is_student(user):
    try:
        return user.profile.is_student
    except:
        return False


def is_parent(user):
    try:
        return user.profile.role == 'parent'
    except:
        return False


@login_required
def grade_forecast_view(request):
    student = None
    if is_student(request.user):
        try:
            student = request.user.student_profile
        except:
            pass
    elif is_parent(request.user):
        try:
            parent = request.user.parent_profile
            # Let's take first child for demo
            link = ParentStudentLink.objects.filter(parent=parent).first()
            if link:
                student = link.student
        except:
            pass

    forecasts = []
    what_if = []
    if student:
        forecasts = GradeForecast.objects.filter(student=student)
        what_if = WhatIfScenario.objects.filter(student=student)

    context = {
        'student': student,
        'forecasts': forecasts,
        'what_if': what_if
    }
    return render(request, 'advanced_features/grade_forecast.html', context)


@login_required
def learning_path_view(request):
    student = None
    if is_student(request.user):
        try:
            student = request.user.student_profile
        except:
            pass
    elif is_parent(request.user):
        try:
            parent = request.user.parent_profile
            link = ParentStudentLink.objects.filter(parent=parent).first()
            if link:
                student = link.student
        except:
            pass

    learning_paths = []
    resources = []
    if student:
        learning_paths = PersonalizedLearningPath.objects.filter(student=student).select_related('subject')
        # Get all resources related to student's subjects
        resources = LearningResource.objects.filter(subject__in=[lp.subject for lp in learning_paths])

    context = {
        'student': student,
        'learning_paths': learning_paths,
        'resources': resources
    }
    return render(request, 'advanced_features/learning_path.html', context)


@login_required
def gamification_view(request):
    student = None
    if is_student(request.user):
        try:
            student = request.user.student_profile
        except:
            pass

    leaderboard = Student.objects.annotate(
        total_points=Sum('points__points')
    ).order_by('-total_points')[:10]

    badges = []
    points_history = []
    total_points = 0
    if student:
        badges = StudentBadge.objects.filter(student=student).select_related('badge')
        points_history = StudentPoint.objects.filter(student=student).order_by('-created_at')[:10]
        total_points = points_history.aggregate(total=Sum('points'))['total'] or 0

    context = {
        'student': student,
        'leaderboard': leaderboard,
        'badges': badges,
        'points_history': points_history,
        'total_points': total_points
    }
    return render(request, 'advanced_features/gamification.html', context)


@login_required
def calendar_view(request):
    events = Event.objects.filter(
        start_datetime__gte=timezone.now() - timedelta(days=7)
    ).order_by('start_datetime')[:30]

    context = {
        'events': events
    }
    return render(request, 'advanced_features/calendar.html', context)


@login_required
def parent_portal_view(request):
    if not is_parent(request.user):
        messages.error(request, "You don't have permission to access the guardian portal.")
        return redirect('home')

    try:
        parent = request.user.parent_profile
    except:
        messages.error(request, "Guardian profile not found.")
        return redirect('home')

    children = ParentStudentLink.objects.filter(parent=parent).select_related('student')

    context = {
        'parent': parent,
        'children': children
    }
    return render(request, 'advanced_features/parent_portal.html', context)


@login_required
def progress_report_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    reports = ProgressReport.objects.filter(student=student).order_by('-report_date')

    # Check permission
    if is_student(request.user):
        try:
            if request.user.student_profile != student:
                messages.error(request, "You don't have permission.")
                return redirect('home')
        except:
            messages.error(request, "Permission denied.")
            return redirect('home')
    elif is_parent(request.user):
        try:
            parent = request.user.parent_profile
            if not ParentStudentLink.objects.filter(parent=parent, student=student).exists():
                messages.error(request, "You don't have permission.")
                return redirect('home')
        except:
            messages.error(request, "Permission denied.")
            return redirect('home')

    context = {
        'student': student,
        'reports': reports
    }
    return render(request, 'advanced_features/progress_reports.html', context)


@login_required
def ptm_scheduler_view(request):
    if is_parent(request.user):
        try:
            parent = request.user.parent_profile
        except:
            messages.error(request, "Parent profile not found.")
            return redirect('home')
        meetings = ParentTeacherMeeting.objects.filter(parent=parent).order_by('-meeting_date')
    elif is_teacher(request.user):
        meetings = ParentTeacherMeeting.objects.filter(teacher=request.user).order_by('-meeting_date')
    else:
        messages.error(request, "You don't have permission.")
        return redirect('home')

    context = {
        'meetings': meetings
    }
    return render(request, 'advanced_features/ptm_scheduler.html', context)
