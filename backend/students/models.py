from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Semester(models.Model):
    SEMESTER_CHOICES = (
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    )

    name = models.CharField(max_length=50)
    semester_type = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'academic_year')
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
        ordering = ['-academic_year__start_date', 'semester_type']

    def __str__(self):
        return f"{self.name} {self.academic_year.name}"


class ClassSection(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_sections')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Class Section'
        verbose_name_plural = 'Class Sections'
        unique_together = ('name', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.name} - {self.academic_year.name if self.academic_year else 'No Year'}"


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    credit_hours = models.IntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    class_section = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    PROGRAM_CHOICES = (
        ('bsc', 'Bachelor of Science (BSc)'),
        ('btech', 'Bachelor of Technology (BTech)'),
        ('ba', 'Bachelor of Arts (BA)'),
        ('bcom', 'Bachelor of Commerce (BCom)'),
        ('msc', 'Master of Science (MSc)'),
        ('mtech', 'Master of Technology (MTech)'),
        ('ma', 'Master of Arts (MA)'),
        ('phd', 'Doctor of Philosophy (PhD)'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=30, blank=True, null=True)  # University roll number
    program = models.CharField(max_length=20, choices=PROGRAM_CHOICES, default='bsc')  # BSc/MSc/PhD etc.
    year = models.IntegerField(blank=True, null=True)  # 1st/2nd/3rd/4th year
    specialization = models.CharField(max_length=100, blank=True, null=True)  # e.g., Computer Science, Physics
    thesis_topic = models.TextField(blank=True, null=True)  # For Masters/PhD students
    enrollment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    attendance = models.FloatField(default=0)
    cgpa = models.FloatField(default=0.0)  # Cumulative Grade Point Average
    marks = models.FloatField(default=0)  # For backward compatibility
    report = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentEnrollment(models.Model):
    ENROLLMENT_STATUS = (
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ENROLLMENT_STATUS, default='enrolled')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.code}"


class Exam(models.Model):
    EXAM_TYPES = (
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('lab', 'Lab Work'),
        ('thesis', 'Thesis Evaluation'),
        ('research_paper', 'Research Paper'),
        ('presentation', 'Presentation'),
    )

    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    total_marks = models.FloatField(default=100)
    date = models.DateField()
    exam_type = models.CharField(max_length=15, choices=EXAM_TYPES, default='midterm')

    def __str__(self):
        return f"{self.name} ({self.exam_type})"


class Result(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.FloatField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}"

    def save(self, *args, **kwargs):
        if not self.grade:
            percentage = (self.marks_obtained / self.exam.total_marks) * 100
            if percentage >= 90:
                self.grade = 'A+'
            elif percentage >= 80:
                self.grade = 'A'
            elif percentage >= 70:
                self.grade = 'B+'
            elif percentage >= 60:
                self.grade = 'B'
            elif percentage >= 50:
                self.grade = 'C+'
            elif percentage >= 40:
                self.grade = 'C'
            elif percentage >= 30:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='present')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.date}: {self.status}"


class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='given_feedback')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} -> {self.teacher.username}: {self.rating}/5"