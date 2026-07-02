
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from advanced_features.models import Parent, ParentStudentLink
from students.models import Student

print("Fixing parent user...")

# Create or get user
user, created = User.objects.get_or_create(username='parent_demo')
user.set_password('parent1234')
user.save()
print(f"User 'parent_demo' {'created' if created else 'updated'} with password 'parent1234'")

# Create or update profile
profile, p_created = UserProfile.objects.update_or_create(
    user=user,
    defaults={'role': 'parent', 'phone': '123-456-7890', 'bio': 'Demo parent account'}
)
print(f"Profile {'created' if p_created else 'updated'}, role: {profile.role}")

# Create or update Parent record
parent, pa_created = Parent.objects.update_or_create(
    user=user,
    defaults={'name': 'John Parent', 'phone': '123-456-7890', 'email': 'parent@example.com'}
)
print(f"Parent record {'created' if pa_created else 'updated'}")

# Link to first student
student = Student.objects.first()
if student:
    link, l_created = ParentStudentLink.objects.get_or_create(parent=parent, student=student)
    print(f"Linked to student: {student.name} {'(new link)' if l_created else ''}")
else:
    print("No students found to link!")

print("\nParent login credentials:")
print("Username: parent_demo")
print("Password: parent1234")
