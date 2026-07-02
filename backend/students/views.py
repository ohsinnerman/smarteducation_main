from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .models import Student, Course, Subject, Exam, Result, AttendanceRecord, StudentEnrollment, Feedback
from advanced_features.models import Parent, ParentStudentLink


def is_admin(user):
    """Check if user has admin role."""
    try:
        return user.profile.role == 'admin'
    except Exception:
        return False


def is_teacher(user):
    """Check if user has teacher role."""
    try:
        return user.profile.role == 'teacher'
    except Exception:
        return False


@login_required
def home(request):
    """Student list with search and filter."""
    # Admin sees all; teacher sees their course students; parent sees linked students; students see only themselves
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if is_admin(request.user):
        students = Student.objects.all()
    elif role == 'teacher':
        students = Student.objects.filter(enrollments__course__teacher=request.user).distinct()
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            students = Student.objects.filter(id__in=linked_ids)
        else:
            students = Student.objects.none()
    else:
        try:
            student = request.user.student_profile
        except Exception:
            student = None
        if student:
            students = Student.objects.filter(pk=student.pk)
        else:
            students = Student.objects.none()

    # Search
    search_query = request.GET.get('q', '')
    if search_query and is_admin(request.user):
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(program__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )

    # Filters
    program_filter = request.GET.get('program', '')
    if program_filter and is_admin(request.user):
        students = students.filter(program=program_filter)

    year_filter = request.GET.get('year', '')
    if year_filter and is_admin(request.user):
        students = students.filter(year=year_filter)

    status_filter = request.GET.get('status', '')
    if status_filter and is_admin(request.user):
        students = students.filter(status=status_filter)

    attendance_min = request.GET.get('attendance_min', '')
    if attendance_min and is_admin(request.user):
        students = students.filter(attendance__gte=float(attendance_min))

    marks_min = request.GET.get('marks_min', '')
    if marks_min and is_admin(request.user):
        students = students.filter(marks__gte=float(marks_min))

    context = {
        'students': students,
        'search_query': search_query,
        'program_filter': program_filter,
        'year_filter': year_filter,
        'status_filter': status_filter,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_create(request):
    """Add a new student - admin only."""
    if not is_admin(request.user):
        return redirect('student_list')
        
    if request.method == 'POST':
        name = request.POST['name']
        program = request.POST.get('program', 'bsc')
        year = request.POST.get('year', None)
        specialization = request.POST.get('specialization', '')
        attendance = request.POST.get('attendance', 0)
        marks = request.POST.get('marks', 0)
        report = request.FILES.get('report')

        Student.objects.create(
            name=name,
            program=program,
            year=year or None,
            specialization=specialization or None,
            attendance=attendance,
            marks=marks,
            report=report
        )
        return redirect('student_list')

    return render(request, 'students/student_form.html')


@login_required
def student_detail(request, pk):
    """View student details."""
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student)
    attendance_records = AttendanceRecord.objects.filter(student=student)[:20]
    enrollments = StudentEnrollment.objects.filter(student=student)
    feedback_given = Feedback.objects.filter(student=student)

    context = {
        'student': student,
        'results': results,
        'attendance_records': attendance_records,
        'enrollments': enrollments,
        'feedback_given': feedback_given,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_update(request, pk):
    """Update student record - admin only."""
    if not is_admin(request.user):
        return redirect('student_list')
        
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.name = request.POST.get('name', student.name)
        student.program = request.POST.get('program', student.program)
        student.year = request.POST.get('year', student.year)
        student.specialization = request.POST.get('specialization', student.specialization)
        student.attendance = request.POST.get('attendance', student.attendance)
        student.marks = request.POST.get('marks', student.marks)
        student.status = request.POST.get('status', student.status)
        if 'report' in request.FILES:
            student.report = request.FILES['report']
        student.save()
        return redirect('student_detail', pk=student.pk)

    context = {'student': student}
    return render(request, 'students/student_form.html', context)


@login_required
def student_delete(request, pk):
    """Delete student record - admin only."""
    if not is_admin(request.user):
        return redirect('student_list')
        
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    context = {'student': student}
    return render(request, 'students/student_confirm_delete.html', context)


# Course views
@login_required
def course_list(request):
    # Allow teachers to see their courses, parents to see linked students' courses, and students to browse/enroll courses
    search_query = request.GET.get('q', '')
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    enrolled_course_ids = []
    student = None
    if role == 'student':
        try:
            student = request.user.student_profile
        except Exception:
            student = None

    if is_admin(request.user):
        courses = Course.objects.all()
    elif role == 'teacher':
        courses = Course.objects.filter(teacher=request.user)
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            courses = Course.objects.filter(enrollments__student_id__in=linked_ids).distinct()
        else:
            courses = Course.objects.none()
    elif student is not None:
        enrolled_course_ids = list(StudentEnrollment.objects.filter(student=student, status='enrolled').values_list('course_id', flat=True))
        courses = Course.objects.all()
    else:
        courses = Course.objects.none()

    if search_query:
        courses = courses.filter(Q(name__icontains=search_query) | Q(code__icontains=search_query))

    return render(request, 'students/course_list.html', {
        'courses': courses,
        'search_query': search_query,
        'is_admin': is_admin(request.user),
        'enrolled_course_ids': enrolled_course_ids,
        'role': role,
    })


@login_required
def course_create(request):
    """Create course - admin only."""
    if not is_admin(request.user):
        return redirect('course_list')
        
    if request.method == 'POST':
        Course.objects.create(
            name=request.POST['name'],
            code=request.POST['code'],
            description=request.POST.get('description', ''),
            teacher=request.user if request.user.profile.role == 'teacher' else None,
            credit_hours=request.POST.get('credit_hours', 3),
        )
        return redirect('course_list')
    return render(request, 'students/course_form.html')


@login_required
def course_enroll(request, pk):
    """Allow a student to enroll in a course from the student portal."""
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if role != 'student':
        return redirect('course_list')

    try:
        student = request.user.student_profile
    except Exception:
        student = None

    course = get_object_or_404(Course, pk=pk)
    if student:
        StudentEnrollment.objects.get_or_create(student=student, course=course, defaults={'status': 'enrolled'})
    return redirect('course_list')


# Exam views
@login_required
def exam_list(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if is_admin(request.user):
        exams = Exam.objects.select_related('subject').all()
    elif role == 'teacher':
        exams = Exam.objects.filter(subject__course__teacher=request.user).select_related('subject').distinct()
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            exams = Exam.objects.filter(subject__course__enrollments__student_id__in=linked_ids).select_related('subject').distinct()
        else:
            exams = Exam.objects.none()
    else:
        try:
            student = request.user.student_profile
        except Exception:
            student = None
        if student:
            enrolled_course_ids = student.enrollments.filter(status='enrolled').values_list('course_id', flat=True)
            exams = Exam.objects.filter(subject__course_id__in=enrolled_course_ids).select_related('subject').distinct()
        else:
            exams = Exam.objects.none()
    return render(request, 'students/exam_list.html', {'exams': exams, 'is_admin': is_admin(request.user)})


@login_required
def exam_create(request):
    """Create exam - admin or teacher."""
    if not (is_admin(request.user) or is_teacher(request.user)):
        return redirect('exam_list')

    if request.method == 'POST':
        Exam.objects.create(
            name=request.POST['name'],
            subject_id=request.POST['subject'],
            total_marks=request.POST.get('total_marks', 100),
            date=request.POST['date'],
            exam_type=request.POST.get('exam_type', 'midterm'),
        )
        return redirect('exam_list')

    if is_teacher(request.user):
        subjects = Subject.objects.filter(course__teacher=request.user)
    else:
        subjects = Subject.objects.all()
    return render(request, 'students/exam_form.html', {'subjects': subjects})


@login_required
def exam_update(request, pk):
    """Update exam - admin or teacher."""
    try:
        exam = Exam.objects.select_related('subject__course').get(pk=pk)
    except Exam.DoesNotExist:
        return redirect('exam_list')

    if not (is_admin(request.user) or (is_teacher(request.user) and exam.subject.course.teacher == request.user)):
        return redirect('exam_list')

    if request.method == 'POST':
        exam.name = request.POST['name']
        exam.subject_id = request.POST['subject']
        exam.total_marks = request.POST.get('total_marks', 100)
        exam.date = request.POST['date']
        exam.exam_type = request.POST.get('exam_type', 'midterm')
        exam.save()
        return redirect('exam_list')

    if is_teacher(request.user):
        subjects = Subject.objects.filter(course__teacher=request.user)
    else:
        subjects = Subject.objects.all()
    return render(request, 'students/exam_form.html', {'subjects': subjects, 'exam': exam})


# Result views
@login_required
def result_list(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if is_admin(request.user):
        results = Result.objects.select_related('student', 'exam').all()
    elif role == 'teacher':
        results = Result.objects.filter(exam__subject__course__teacher=request.user).select_related('student', 'exam')
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            results = Result.objects.filter(student_id__in=linked_ids).select_related('student', 'exam')
        else:
            results = Result.objects.none()
    else:
        try:
            student = request.user.student_profile
        except Exception:
            student = None
        if student:
            results = Result.objects.filter(student=student).select_related('student', 'exam')
        else:
            results = Result.objects.none()
    search_query = request.GET.get('q', '')
    if search_query and is_admin(request.user):
        results = results.filter(student__name__icontains=search_query)

    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        results = results.filter(grade=grade_filter)

    return render(request, 'students/result_list.html', {
        'results': results,
        'search_query': search_query,
        'is_admin': is_admin(request.user),
    })


@login_required
def result_create(request):
    """Create result - admin only."""
    if not is_admin(request.user):
        return redirect('result_list')
        
    if request.method == 'POST':
        Result.objects.create(
            student_id=request.POST['student'],
            exam_id=request.POST['exam'],
            marks_obtained=request.POST['marks_obtained'],
            remarks=request.POST.get('remarks', ''),
        )
        return redirect('result_list')
    students = Student.objects.filter(status='active')
    exams = Exam.objects.all()
    return render(request, 'students/result_form.html', {'students': students, 'exams': exams})


# Attendance views
@login_required
def attendance_list(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if is_admin(request.user):
        records = AttendanceRecord.objects.select_related('student', 'subject').all()
    elif role == 'teacher':
        records = AttendanceRecord.objects.filter(subject__course__teacher=request.user).select_related('student', 'subject')
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            records = AttendanceRecord.objects.filter(student_id__in=linked_ids).select_related('student', 'subject')
        else:
            records = AttendanceRecord.objects.none()
    else:
        try:
            student = request.user.student_profile
        except Exception:
            student = None
        if student:
            records = AttendanceRecord.objects.filter(student=student).select_related('student', 'subject')
        else:
            records = AttendanceRecord.objects.none()
    search_query = request.GET.get('q', '')
    if search_query and is_admin(request.user):
        records = records.filter(student__name__icontains=search_query)

    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)

    return render(request, 'students/attendance_list.html', {
        'records': records,
        'search_query': search_query,
        'is_admin': is_admin(request.user),
    })


@login_required
def attendance_create(request):
    """Create attendance - admin or teacher."""
    if not (is_admin(request.user) or is_teacher(request.user)):
        return redirect('attendance_list')

    if request.method == 'POST':
        AttendanceRecord.objects.create(
            student_id=request.POST['student'],
            subject_id=request.POST['subject'],
            date=request.POST['date'],
            status=request.POST['status'],
        )
        return redirect('attendance_list')

    if is_teacher(request.user):
        subjects = Subject.objects.filter(course__teacher=request.user)
        students = Student.objects.filter(enrollments__course__teacher=request.user, status='active').distinct()
    else:
        students = Student.objects.filter(status='active')
        subjects = Subject.objects.all()
    return render(request, 'students/attendance_form.html', {'students': students, 'subjects': subjects})


@login_required
def attendance_update(request, pk):
    """Update attendance - admin or teacher."""
    try:
        record = AttendanceRecord.objects.select_related('subject__course').get(pk=pk)
    except AttendanceRecord.DoesNotExist:
        return redirect('attendance_list')

    if not (is_admin(request.user) or (is_teacher(request.user) and record.subject.course.teacher == request.user)):
        return redirect('attendance_list')

    if request.method == 'POST':
        record.student_id = request.POST['student']
        record.subject_id = request.POST['subject']
        record.date = request.POST['date']
        record.status = request.POST['status']
        record.save()
        return redirect('attendance_list')

    if is_teacher(request.user):
        subjects = Subject.objects.filter(course__teacher=request.user)
        students = Student.objects.filter(enrollments__course__teacher=request.user, status='active').distinct()
    else:
        students = Student.objects.filter(status='active')
        subjects = Subject.objects.all()
    return render(request, 'students/attendance_form.html', {'students': students, 'subjects': subjects, 'record': record})


# Feedback views
@login_required
def feedback_list(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = None

    if is_admin(request.user):
        feedbacks = Feedback.objects.select_related('student', 'teacher').all()
    elif role == 'teacher':
        feedbacks = Feedback.objects.filter(teacher=request.user).select_related('student', 'teacher')
    elif role == 'parent':
        parent = Parent.objects.filter(user=request.user).first()
        if parent:
            linked_ids = ParentStudentLink.objects.filter(parent=parent).values_list('student_id', flat=True)
            feedbacks = Feedback.objects.filter(student_id__in=linked_ids).select_related('student', 'teacher')
        else:
            feedbacks = Feedback.objects.none()
    else:
        try:
            student = request.user.student_profile
        except Exception:
            student = None
        if student:
            feedbacks = Feedback.objects.filter(student=student).select_related('student', 'teacher')
        else:
            feedbacks = Feedback.objects.none()
    return render(request, 'students/feedback_list.html', {'feedbacks': feedbacks, 'is_admin': is_admin(request.user)})


@login_required
def feedback_create(request):
    """Create feedback - admin only."""
    if not is_admin(request.user):
        return redirect('feedback_list')
        
    if request.method == 'POST':
        student = Student.objects.get(pk=request.POST['student'])
        Feedback.objects.create(
            student=student,
            teacher_id=request.POST['teacher'],
            rating=request.POST['rating'],
            comment=request.POST.get('comment', ''),
        )
        return redirect('feedback_list')
    students = Student.objects.filter(status='active')
    from django.contrib.auth.models import User
    teachers = User.objects.filter(profile__role='teacher')
    return render(request, 'students/feedback_form.html', {'students': students, 'teachers': teachers})