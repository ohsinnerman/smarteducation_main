# Smart Education System

A Django-based smart education platform for managing students, teachers, parents, dashboards, notifications, and AI-assisted analytics.

## Features
- Role-based dashboards for admin, teacher, student, and parent users
- Student, course, subject, attendance, and result management
- Notification and email integration
- Demo accounts for quick testing
- Basic AI/ML prediction support

## Project Structure
- `smarteducation/` — main Django project
- `smarteducation/accounts/` — authentication and role-based login flow
- `smarteducation/dashboards/` — dashboard views and templates
- `smarteducation/students/` — student and academic data management
- `smarteducation/notifications/` — notifications and email integration
- `smarteducation/ml/` — ML-related models and prediction logic

## Tech Stack
- Python 3.11+
- Django 5.2+
- SQLite (development)
- Bootstrap-based templates

## Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd smart_education_system-main
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r smarteducation/requirements.txt
```

### 4. Apply migrations and run the server
```bash
cd smarteducation
python manage.py migrate
python manage.py runserver
```

## Demo Credentials
After starting the app, the following demo accounts are available:
- Admin: `admin_demo` / `admin1234`
- Teacher: `teacher_demo` / `teacher1234`
- Student 1: `student_demo1` / `student1234`
- Student 2: `student_demo2` / `student1234`
- Student 3: `student_demo3` / `student1234`
- Parent: `parent_demo` / `parent1234`

## Notes
- The project is currently configured for local development and can be adapted for production deployment.
- For AWS deployment, configure environment variables and a production database before publishing.
