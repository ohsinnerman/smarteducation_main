from django.contrib import admin
from .models import (
    Department,
    AcademicYear,
    Semester,
    ClassSection,
    Course,
    Subject,
    Student,
    StudentEnrollment,
    Exam,
    Result,
    AttendanceRecord,
    Feedback,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('name', 'code')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester_type', 'academic_year', 'start_date', 'end_date', 'active')
    list_filter = ('semester_type', 'academic_year', 'active')
    search_fields = ('name',)


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'academic_year', 'semester', 'teacher')
    list_filter = ('department', 'academic_year', 'semester')
    search_fields = ('name',)


class StudentEnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 1
    autocomplete_fields = ('student', 'course')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'department', 'academic_year', 'semester', 'class_section', 'credit_hours', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('teacher', 'department', 'academic_year', 'semester')
    inlines = [StudentEnrollmentInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course', 'department')
    search_fields = ('name', 'code')
    list_filter = ('course', 'department')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'program', 'year', 'specialization', 'status', 'attendance', 'cgpa', 'created_at')
    search_fields = ('name', 'roll_number', 'specialization')
    list_filter = ('status', 'program', 'year')
    inlines = [StudentEnrollmentInline]


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_date', 'status')
    list_filter = ('status', 'course')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'exam_type', 'total_marks', 'date')
    list_filter = ('exam_type', 'subject__course')
    search_fields = ('name',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade', 'created_at')
    list_filter = ('grade',)
    search_fields = ('student__name',)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status')
    list_filter = ('status', 'date', 'subject')
    search_fields = ('student__name',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'rating', 'created_at')
    list_filter = ('rating',)