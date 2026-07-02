
from django.db import models
from django.contrib.auth.models import User
from students.models import Student, Subject, Course
from django.utils import timezone


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Parent"


class ParentStudentLink(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parent', 'student')

    def __str__(self):
        return f"{self.parent.name} -> {self.student.name}"


class GradeForecast(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grade_forecasts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grade_forecasts')
    predicted_marks = models.FloatField()
    confidence_score = models.FloatField()
    forecast_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.predicted_marks}"


class WhatIfScenario(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='what_if_scenarios')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='what_if_scenarios')
    attendance_change_pct = models.FloatField(help_text="Percentage change in attendance")
    marks_change_pct = models.FloatField(help_text="Percentage change in marks")
    predicted_new_marks = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: What If?"


class LearningResource(models.Model):
    RESOURCE_TYPES = (
        ('video', 'Video'),
        ('article', 'Article'),
        ('practice', 'Practice Exercise'),
        ('course', 'Full Course'),
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField()
    difficulty_level = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3)
    provider = models.CharField(max_length=100, default='Khan Academy', help_text="e.g., Khan Academy, Coursera")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.provider}"


class PersonalizedLearningPath(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_paths')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='learning_paths')
    resources = models.ManyToManyField(LearningResource, related_name='learning_paths', blank=True)
    weak_topics = models.TextField(help_text="Comma-separated list of weak topics")
    recommended_study_hours = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} Learning Path"


class Badge(models.Model):
    BADGE_TYPES = (
        ('attendance', 'Attendance'),
        ('performance', 'Performance'),
        ('improvement', 'Improvement'),
        ('participation', 'Participation'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    icon = models.CharField(max_length=50, default='bi-trophy', help_text="Bootstrap Icon class")
    points_required = models.IntegerField(default=0, help_text="Points needed to earn this badge (0 for milestone)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='student_badges')
    earned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'badge')

    def __str__(self):
        return f"{self.student.name} - {self.badge.name}"


class StudentPoint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=[('attendance', 'Attendance'), ('marks', 'Marks'), ('participation', 'Participation'), ('other', 'Other')], default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name}: +{self.points} points ({self.reason})"


class Event(models.Model):
    EVENT_TYPES = (
        ('class', 'Class'),
        ('exam', 'Exam'),
        ('meeting', 'Meeting'),
        ('assignment', 'Assignment'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    related_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    google_event_id = models.CharField(max_length=255, blank=True, null=True)
    outlook_event_id = models.CharField(max_length=255, blank=True, null=True)
    is_reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.start_datetime}"


class EventAttendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_attending')
    is_attending = models.BooleanField(default=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class ParentTeacherMeeting(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='meetings')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_meetings')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ptm_meetings')
    meeting_date = models.DateTimeField()
    meeting_link = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PTM - {self.student.name} - {self.meeting_date}"


class ProgressReport(models.Model):
    REPORT_TYPES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    report_date = models.DateField()
    attendance_pct = models.FloatField()
    avg_marks = models.FloatField()
    weak_subjects = models.TextField(blank=True, null=True)
    strong_subjects = models.TextField(blank=True, null=True)
    teacher_comments = models.TextField(blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.report_type} Report ({self.report_date})"
