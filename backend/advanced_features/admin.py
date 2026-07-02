
from django.contrib import admin
from .models import (
    Parent, ParentStudentLink,
    GradeForecast, WhatIfScenario,
    LearningResource, PersonalizedLearningPath,
    Badge, StudentBadge, StudentPoint,
    Event, EventAttendee,
    ParentTeacherMeeting, ProgressReport
)


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email', 'phone']


@admin.register(ParentStudentLink)
class ParentStudentLinkAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student']
    list_filter = ['parent', 'student']


@admin.register(GradeForecast)
class GradeForecastAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'predicted_marks', 'confidence_score', 'forecast_date']
    list_filter = ['subject', 'forecast_date']
    search_fields = ['student__name', 'subject__name']


@admin.register(WhatIfScenario)
class WhatIfScenarioAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'attendance_change_pct', 'predicted_new_marks']
    list_filter = ['subject']
    search_fields = ['student__name', 'subject__name']


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'resource_type', 'provider', 'difficulty_level']
    list_filter = ['subject', 'resource_type', 'provider', 'difficulty_level']
    search_fields = ['title', 'description']


@admin.register(PersonalizedLearningPath)
class PersonalizedLearningPathAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'recommended_study_hours', 'updated_at']
    list_filter = ['subject', 'updated_at']
    search_fields = ['student__name', 'subject__name']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'points_required']
    list_filter = ['badge_type']
    search_fields = ['name', 'description']


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ['student', 'badge', 'earned_date']
    list_filter = ['badge', 'earned_date']
    search_fields = ['student__name', 'badge__name']


@admin.register(StudentPoint)
class StudentPointAdmin(admin.ModelAdmin):
    list_display = ['student', 'points', 'category', 'reason', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['student__name', 'reason']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_datetime', 'end_datetime', 'created_by']
    list_filter = ['event_type', 'start_datetime']
    search_fields = ['title', 'description']


@admin.register(EventAttendee)
class EventAttendeeAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'is_attending']
    list_filter = ['is_attending']
    search_fields = ['user__username', 'event__title']


@admin.register(ParentTeacherMeeting)
class ParentTeacherMeetingAdmin(admin.ModelAdmin):
    list_display = ['parent', 'teacher', 'student', 'meeting_date', 'status']
    list_filter = ['status', 'meeting_date']
    search_fields = ['parent__name', 'teacher__username', 'student__name']


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'report_type', 'report_date', 'attendance_pct', 'avg_marks', 'is_sent']
    list_filter = ['report_type', 'report_date', 'is_sent']
    search_fields = ['student__name']
