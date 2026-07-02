from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .models import UserProfile
from notifications.email import send_welcome_email


# SIGNUP
@csrf_protect
@ensure_csrf_cookie
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '')
        role = request.POST.get('role', 'student')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        # Create user profile with role
        UserProfile.objects.create(user=user, role=role)

        # Send welcome email
        if email:
            send_welcome_email(user)

        return redirect('/login/')

    return render(request, 'signup.html')


# LOGIN
LOGIN_ROLES = {
    'admin': 'Admin Login',
    'teacher': 'Teacher Login',
    'student': 'Student Login',
    'parent': 'Parent Login',
}


def redirect_to_role_dashboard(role):
    if role == 'admin':
        return redirect('/dashboards/admin/')
    if role == 'teacher':
        return redirect('/dashboards/teacher/')
    return redirect('/dashboards/student/')


@csrf_protect
@ensure_csrf_cookie
def login_view(request, required_role=None):
    login_title = LOGIN_ROLES.get(required_role, 'Login')
    selected_role = required_role
    form_action = request.path

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        selected_role = request.POST.get('selected_role') or selected_role

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:
            try:
                actual_role = user.profile.role
            except UserProfile.DoesNotExist:
                actual_role = 'student'

            effective_role = selected_role or required_role or actual_role

            if effective_role and actual_role != effective_role:
                return render(request, 'login.html', {
                    'error': f'Invalid role selection. This account is a {actual_role.capitalize()}.',
                    'selected_role': effective_role,
                    'login_title': login_title,
                    'form_action': form_action,
                })

            login(request, user)
            return redirect_to_role_dashboard(actual_role)

        return render(request, 'login.html', {
            'error': 'Invalid username or password.',
            'selected_role': selected_role,
            'login_title': login_title,
            'form_action': form_action,
        })

    return render(request, 'login.html', {
        'selected_role': selected_role,
        'login_title': login_title,
        'form_action': form_action,
    })


def admin_login_view(request):
    return login_view(request, required_role='admin')


def teacher_login_view(request):
    return login_view(request, required_role='teacher')


def student_login_view(request):
    return login_view(request, required_role='student')


def parent_login_view(request):
    return login_view(request, required_role='parent')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/login/')


# PROFILE
@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.phone = request.POST.get('phone', profile.phone or '')
        profile.bio = request.POST.get('bio', profile.bio or '')
        profile.department = request.POST.get('department', profile.department or '')

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()
        return redirect('profile')

    context = {
        'profile': profile,
    }
    return render(request, 'profile_edit.html', context)