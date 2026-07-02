# Smart Education Analytics Platform

Role-based student analytics: dashboards for admin / teacher / student / parent,
attendance & results tracking, ML at-risk prediction, gamification, calendar,
grade forecasts, learning paths, and parent–teacher meetings.

**Architecture:** API-only Django backend + separate React frontend. See
[ARCHITECTURE.md](ARCHITECTURE.md).

```
smarteducation/
├── backend/     Django + DRF REST API (+ admin). Postgres in prod, SQLite in dev.
├── frontend/    React + Vite SPA. Consumes the API over VITE_API_BASE_URL.
├── AUDIT.md · ARCHITECTURE.md · DEPLOYMENT_GUIDE.md · WALL_OF_SHAME.md
```

## Local setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit as needed; SQLite works with no DB config
python manage.py migrate
python manage.py seed_demo_data # creates demo users + full demo dataset
python manage.py diagnose_env   # shows which integrations are configured
python manage.py runserver      # http://localhost:8000
```

**On a completely fresh database, the full path is:**
`migrate` → `seed_demo_data` (→ optional `reset_predictions --train` for ML).
`seed_demo_data` is idempotent and safe to re-run.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # set VITE_API_BASE_URL=http://localhost:8000/api
npm run dev                     # http://localhost:5173
```

## Demo credentials

| Role    | Username                | Password      |
|---------|-------------------------|---------------|
| Admin   | `admin_demo`            | `admin1234`   |
| Teacher | `teacher_demo`          | `teacher1234` |
| Student | `student_demo1` (2, 3)  | `student1234` |
| Parent  | `parent_demo`           | `parent1234`  |

## Management commands

- `python manage.py seed_demo_data` — idempotent demo/academic data seed.
- `python manage.py reset_predictions [--train] [--clear-only]` — ML predictions.
- `python manage.py diagnose_env` — report resolved config + which optional
  integrations (email/Twilio/OpenAI) are on/off. Run this in deploys.

## Configuration

All backend config comes from `backend/.env` (see `.env.example` for the full,
annotated list). In `DJANGO_ENV=production`, missing `DJANGO_SECRET_KEY`,
`DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, or `CORS_ALLOWED_ORIGINS` is a hard
startup failure — no silent dev fallbacks. Optional integrations log a loud
warning when unset rather than silently no-op-ing.

## Deployment

Backend → EC2 + docker-compose (+ RDS); frontend → Vercel/Netlify. Full
copy-pasteable guide in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
