# Smart Education Analytics Platform

Role-based student analytics: dashboards for admin / teacher / student / parent,
attendance & results tracking, ML at-risk prediction, gamification, calendar,
grade forecasts, learning paths, and parent–teacher meetings.

**Architecture:** API-only Django backend + separate React frontend. See the
[ARCHITECTURE.md](ARCHITECTURE.md).

**Live demo:** frontend on Vercel (`https://smarteducation-main.vercel.app`) →
backend on AWS EC2 behind HTTPS (`https://smartedu14783.duckdns.org/api`). Log in
with any demo account below.

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

The live demo runs a lightweight, free-tier-friendly setup (SQLite, dummy data):

**Backend — AWS EC2 (t3.micro), Docker Compose, SQLite, HTTPS via Caddy:**

```bash
# on the instance, in backend/
cat > Caddyfile <<'EOF'
smartedu14783.duckdns.org {
    reverse_proxy web:8000
}
EOF
docker compose -f docker-compose.demo.yml up -d --build
docker compose -f docker-compose.demo.yml exec web python manage.py migrate
docker compose -f docker-compose.demo.yml exec web python manage.py seed_demo_data
docker compose -f docker-compose.demo.yml exec web python manage.py reset_predictions --train
```

- `docker-compose.demo.yml` runs Django (gunicorn) + **Caddy**, which auto-provisions
  a free Let's Encrypt cert and terminates HTTPS in front of the app.
- HTTPS requires a hostname you control — a free **DuckDNS** subdomain
  (`smartedu14783.duckdns.org`) points at the EC2 public IP. The AWS default
  `*.compute.amazonaws.com` host cannot get a cert.
- Security group must allow **22 (SSH), 80, 443**.
- `.env` on the box: `DJANGO_ALLOWED_HOSTS=*`, and `CORS_ALLOWED_ORIGINS` set to the
  Vercel origin.

**Frontend — Vercel:**

- Root Directory: `frontend`
- Env var: `VITE_API_BASE_URL=https://smartedu14783.duckdns.org/api`
- `frontend/vercel.json` adds an SPA fallback so client-side routes don't 404 on
  reload. Because the backend is HTTPS, the frontend calls it directly (no proxy,
  no mixed-content block).

For the fuller production path (nginx/RDS/SSM, hardened `DJANGO_ENV=production`), see
[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
