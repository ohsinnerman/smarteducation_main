from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile

ROLE_GROUP_MAP = {
    'admin': 'Admin',
    'teacher': 'Teacher',
    'student': 'Student',
    'parent': 'Parent',
}

TEACHER_PERMISSIONS = [
    'view_course',
    'view_subject',
    'view_student',
    'view_result',
    'view_attendancerecord',
    'view_feedback',
    'add_result',
    'change_result',
    'add_attendancerecord',
    'change_attendancerecord',
    'add_feedback',
    'change_feedback',
]

STUDENT_PERMISSIONS = [
    'view_student',
    'view_result',
    'view_attendancerecord',
    'view_course',
    'view_subject',
    'view_feedback',
]

PARENT_PERMISSIONS = STUDENT_PERMISSIONS


def setup_role_groups():
    # Create groups and assign permissions.
    for group_name in ROLE_GROUP_MAP.values():
        Group.objects.get_or_create(name=group_name)

    admin_group, _ = Group.objects.get_or_create(name='Admin')
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    student_group, _ = Group.objects.get_or_create(name='Student')
    parent_group, _ = Group.objects.get_or_create(name='Parent')

    # Admin has all permissions in the system.
    admin_group.permissions.set(Permission.objects.all())

    # Teacher has access to core academic models and limited result/attendance management.
    teacher_group.permissions.set(Permission.objects.filter(codename__in=TEACHER_PERMISSIONS))

    # Student and parent are view-only for academic records.
    student_group.permissions.set(Permission.objects.filter(codename__in=STUDENT_PERMISSIONS))
    parent_group.permissions.set(Permission.objects.filter(codename__in=PARENT_PERMISSIONS))


@receiver(post_save, sender=UserProfile)
def sync_user_groups(sender, instance, **kwargs):
    role = instance.role
    group_name = ROLE_GROUP_MAP.get(role)
    if not group_name:
        return

    group, _ = Group.objects.get_or_create(name=group_name)
    current_groups = instance.user.groups.all()
    if group not in current_groups or current_groups.count() != 1:
        instance.user.groups.set([group])


def ensure_demo_accounts():
    """Create demo accounts automatically so login credentials work after deployment."""
    demo_users = [
        ('admin_demo', 'admin1234', 'admin'),
        ('teacher_demo', 'teacher1234', 'teacher'),
        ('student_demo1', 'student1234', 'student'),
        ('student_demo2', 'student1234', 'student'),
        ('student_demo3', 'student1234', 'student'),
        ('parent_demo', 'parent1234', 'parent'),
    ]

    for username, password, role in demo_users:
        user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        user.set_password(password)
        user.is_staff = role in {'admin', 'teacher'}
        user.is_superuser = role == 'admin'
        user.save()
        UserProfile.objects.get_or_create(user=user, defaults={'role': role})


@receiver(post_migrate)
def setup_demo_accounts(sender, **kwargs):
    # Gated so demo accounts are never silently created against a real database.
    # Enable explicitly with SEED_DEMO_ACCOUNTS_ON_MIGRATE=true, or use the
    # `seed_demo_data` management command instead.
    from django.conf import settings
    if getattr(settings, "SEED_DEMO_ACCOUNTS_ON_MIGRATE", False):
        ensure_demo_accounts()
