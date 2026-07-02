# Smart Education Analytics Platform - Implementation Plan

## Tech Stack
- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL (production on AWS RDS), SQLite (development)
- **Frontend**: Django Templates + Bootstrap 5 + Chart.js
- **AI/ML**: scikit-learn (predictions) + OpenAI API (generative AI - optional)
- **Notifications**: Django + Celery + Redis (email via SMTP, SMS via Twilio, WhatsApp via Twilio API)
- **Cloud**: AWS (EC2 + RDS + S3 + Elastic Beanstalk or ECS)
- **API**: Django REST Framework

---

## Phase 1: Foundation & Data Models

### Task 1.1 - Enhance User & Profile Models
**File**: `accounts/models.py`
- Create `UserProfile` model linked to Django User with fields: role (Admin/Teacher/Student), phone, avatar, bio, department
- Add role-based user identification (is_admin, is_teacher, is_student properties)

### Task 1.2 - Expand Student Data Models
**File**: `students/models.py`
- Enhance `Student` model: add grade, section, enrollment_date, status (active/inactive), linked user account
- Create `Course` model: name, code, description, teacher (FK), credit_hours
- Create `Subject` model: name, course (FK), code
- Create `StudentEnrollment` model: student (FK), course (FK), enrolled_date, status
- Create `Exam` model: name, subject (FK), total_marks, date, exam_type
- Create `Result` model: student (FK), exam (FK), marks_obtained, grade, remarks
- Create `AttendanceRecord` model: student (FK), date, status (present/absent/late), subject (FK)
- Create `Feedback` model: student (FK), teacher (FK), rating (1-5), comment, created_at

### Task 1.3 - Run Migrations
- Create and apply migrations for all new models
- Register all models in admin.py

---

## Phase 2: Role-Based Authentication & Profile Management

### Task 2.1 - Role-Based Auth
**File**: `accounts/views.py`, `accounts/urls.py`
- Update signup to include role selection
- Add login with role-based redirect (admin->admin dashboard, teacher->teacher dashboard, student->student dashboard)
- Add `@role_required` decorators for access control

### Task 2.2 - Profile Management
**File**: `accounts/views.py`
- Create profile view (view/edit profile)
- Create profile update view (change avatar, phone, bio)
- Update templates with proper forms

### Task 2.3 - Auth Templates
**Files**: `accounts/templates/`
- Redesign `login.html` with Bootstrap 5 styling
- Redesign `signup.html` with role selection
- Create `profile.html` for profile viewing/editing

---

## Phase 3: Built-in Analytics Dashboard (replaces Power BI)

### Task 3.1 - Dashboard App
**Create**: `dashboards/` app
- Create `dashboards/` Django app with views, urls, templates
- Add to `INSTALLED_APPS`

### Task 3.2 - Admin Dashboard
**File**: `dashboards/views.py`
- Overview stats: total students, teachers, courses, avg attendance, avg marks
- User growth chart (Chart.js line chart - monthly registrations)
- Prediction accuracy chart (bar chart - model performance)
- Subject-wise performance (radar chart)
- At-risk students list
- Recent activity feed

### Task 3.3 - Teacher Dashboard
- My courses & student counts
- Attendance trends chart (Chart.js)
- Marks distribution per subject (histogram)
- Students at-risk in my courses
- Quick actions: take attendance, upload marks

### Task 3.4 - Student Dashboard
- My attendance & marks overview
- Performance trend chart (line chart)
- Subject-wise marks (bar chart)
- Upcoming exams
- My feedback/ratings received
- Performance predictions

### Task 3.5 - Dashboard Templates
**Files**: `dashboards/templates/`
- `admin_dashboard.html` - Full analytics with interactive charts
- `teacher_dashboard.html` - Course-focused analytics
- `student_dashboard.html` - Personal performance view
- Use Bootstrap 5 cards, Chart.js for all charts, responsive grid layout

---

## Phase 4: Search & Filter Functionality

### Task 4.1 - Search System
**File**: `students/views.py` or new `search/` module
- Global search across students, courses, subjects
- Filter students by: grade, section, attendance range, marks range, course
- Filter results by: exam, subject, date range, grade
- Pagination for all list views

### Task 4.2 - Search Templates
- Add search bar to navbar (global search)
- Create filter sidebar/filters on list pages
- AJAX-powered live search

---

## Phase 5: AI/ML Module

### Task 5.1 - ML App
**Create**: `ml/` app
- Create `ml/` Django app for all ML functionality
- Add to `INSTALLED_APPS`

### Task 5.2 - Prediction Models
**File**: `ml/predictor.py`
- Student performance prediction (using attendance + past marks)
- At-risk student identification (low attendance + declining marks)
- Dropout prediction
- Store predictions in `PredictionResult` model

### Task 5.3 - Model Training Pipeline
**File**: `ml/training.py`
- Data preprocessing from Django ORM
- Train scikit-learn models (Random Forest, Gradient Boosting)
- Save/load models with joblib
- Management command: `python manage.py train_models`

### Task 5.4 - Prediction API Views
**File**: `ml/views.py`
- View to trigger predictions for students
- View showing prediction accuracy stats (feeds dashboard chart)
- Integration with dashboard views

### Task 5.5 - Generative AI Integration (Optional)
**File**: `ml/genai.py`
- OpenAI API integration for AI insights/recommendations
- Auto-generate student performance summaries
- Suggest interventions for at-risk students
- Configurable on/off via settings

---

## Phase 6: Notification System

### Task 6.1 - Notification Infrastructure
**Create**: `notifications/` app
- `Notification` model: user (FK), title, message, type (email/sms/whatsapp), status, created_at
- `NotificationPreference` model: user (FK), email_enabled, sms_enabled, whatsapp_enabled
- Add to `INSTALLED_APPS`

### Task 6.2 - Email Notifications
**File**: `notifications/email.py`
- Configure Django SMTP (settings.py)
- Email templates: welcome, at-risk alert, exam results, attendance warning
- Send email on: new user signup, at-risk detection, exam result publish

### Task 6.3 - SMS Notifications
**File**: `notifications/sms.py`
- Twilio integration for SMS
- SMS on: at-risk alert, attendance below threshold, exam reminder

### Task 6.4 - WhatsApp Notifications
**File**: `notifications/whatsapp.py`
- Twilio WhatsApp Business API integration
- WhatsApp messages on: at-risk alert, monthly report summary

### Task 6.5 - In-App Notifications
- Notification bell icon in navbar with unread count
- Notification list page with mark-as-read functionality
- Celery + Redis for async notification sending

---

## Phase 7: REST API Layer

### Task 7.1 - API Setup
**File**: `settings.py`, project `urls.py`
- Install and configure Django REST Framework
- Add JWT authentication (djangorestframework-simplejwt)
- Create API URL structure: `/api/v1/`

### Task 7.2 - API Endpoints
**Create**: `api/` app
- Auth: `/api/v1/auth/login/`, `/api/v1/auth/signup/`, `/api/v1/auth/refresh/`
- Students: CRUD `/api/v1/students/`
- Courses: CRUD `/api/v1/courses/`
- Results: CRUD `/api/v1/results/`
- Attendance: CRUD `/api/v1/attendance/`
- Dashboard data: `/api/v1/dashboard/admin/`, `/api/v1/dashboard/teacher/`, `/api/v1/dashboard/student/`
- Predictions: `/api/v1/predictions/`
- Search: `/api/v1/search/?q=...`
- Notifications: `/api/v1/notifications/`
- Feedback: `/api/v1/feedback/`

### Task 7.3 - Serializers & ViewSets
- ModelSerializers for all models
- ReadOnlySerializers for dashboard data
- Filter backends for search/filter API

---

## Phase 8: Feedback & Rating System

### Task 8.1 - Feedback Views
**File**: `students/views.py` or `feedback/` app
- Submit feedback (student rates teacher/course)
- View feedback summary per teacher/course
- Average rating calculation

### Task 8.2 - Feedback Templates
- Feedback form (star rating + comment)
- Feedback summary with average stars

---

## Phase 9: Responsive UI

### Task 9.1 - Base Template
**File**: `templates/base.html`
- Bootstrap 5 navbar with role-based menu items
- Sidebar navigation
- Notification bell with badge
- Search bar in navbar
- User profile dropdown
- Footer

### Task 9.2 - Responsive Pages
- All dashboards: responsive grid (4 cols desktop, 2 cols tablet, 1 col mobile)
- Student list: responsive table with card view on mobile
- Forms: stacked on mobile, inline on desktop
- Charts: responsive resize with Chart.js `responsive: true`

### Task 9.3 - Static Assets
**Files**: `static/css/`, `static/js/`
- Custom CSS variables for theming (blue primary matching current `#001f8f`)
- Common JS utilities (chart helpers, AJAX search, notifications polling)

---

## Phase 10: AWS Cloud Deployment

### Task 10.1 - Production Settings
**File**: `smarteducation/settings.py`
- Split settings: `base.py`, `dev.py`, `prod.py`
- Production: `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`, environment variables via `python-decouple`
- PostgreSQL config for AWS RDS
- AWS S3 for static/media files (django-storages)
- WhiteNoise for static file serving

### Task 10.2 - Docker Setup
**Files**: `Dockerfile`, `docker-compose.yml`
- Multi-stage Dockerfile (Python 3.12, Django, dependencies)
- docker-compose: web + db (Postgres) + redis + celery worker
- `.env.example` for environment variables

### Task 10.3 - AWS Infrastructure
- **EC2** or **Elastic Beanstalk**: Application hosting
- **RDS PostgreSQL**: Managed database
- **S3**: Static files + media uploads
- **ElastiCache**: Redis for Celery + caching
- **SES**: Email sending
- **CloudFront**: CDN for static assets
- **Route 53**: DNS (optional)

### Task 10.4 - CI/CD Pipeline
**File**: `.github/workflows/deploy.yml`
- GitHub Actions: test -> build Docker -> push to ECR -> deploy to ECS/Elastic Beanstalk

---

## File Structure (Final)
```
smarteducation/
├── accounts/          # Auth, profiles, roles
├── students/          # Student CRUD, courses, results, attendance
├── dashboards/        # Analytics dashboards + charts
├── ml/                # AI/ML predictions + generative AI
├── notifications/     # Email, SMS, WhatsApp notifications
├── api/               # REST API layer (DRF)
├── smarteducation/    # Project settings
├── templates/         # Base template (shared layout)
├── static/            # CSS, JS, images
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/
```

---

## Implementation Order
1. Phase 1 (Models) → Phase 2 (Auth) → Phase 9.1 (Base Template)
2. Phase 3 (Dashboards) → Phase 4 (Search/Filter)
3. Phase 7 (API Layer)
4. Phase 5 (AI/ML)
5. Phase 6 (Notifications)
6. Phase 8 (Feedback)
7. Phase 9 (UI Polish)
8. Phase 10 (AWS Deployment)
