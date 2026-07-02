# ARCHITECTURE

The system is now a clean two-tier split: an API-only Django backend and a
separate React frontend that consumes it over HTTPS.

```
┌────────────────────────────┐         ┌──────────────────────────────────┐
│  frontend/  (React + Vite) │         │  backend/  (Django + DRF)        │
│                            │  JSON   │                                  │
│  - JWT login/refresh       │ ──────► │  /api/…      REST endpoints      │
│  - role-routed dashboards  │  HTTPS  │  /api/auth/  JWT obtain/refresh  │
│  - Bootstrap UI (ported    │ ◄────── │  /admin/     Django admin (staff)│
│    from old templates)     │  CORS   │                                  │
│  reads VITE_API_BASE_URL   │         │  Postgres (prod) / SQLite (dev)  │
└────────────────────────────┘         └──────────────────────────────────┘
      hosted anywhere                        one EC2 box (docker-compose)
   (Vercel / Netlify / S3)                   or RDS for the database
```

## Backend (`backend/`)

- **Django REST Framework**, authentication via **JWT**  (`JWTAuthentication`
  first, `SessionAuthentication` retained for the admin site / same-origin).
- **Serves no end-user HTML.** The only templates are Django admin's own (via
  `APP_DIRS` + whitenoise for admin static). All the app-level templates were
  removed in the split.
- **`api/`** exposes every feature as JSON: core academic CRUD (students, courses,
  subjects, exams, results, attendance, enrollments, feedback), notifications &
  preferences, ML predictions, and the previously template-only advanced features
  (parents, grade forecasts, what-if, learning resources/paths, badges, points,
  events, PTM, progress reports). Role dashboards at `/api/dashboard/{admin,
  teacher,student,parent}/` and `/api/me/`.
- **Permissions** reuse the existing `accounts` role system (`UserProfile.role`:
  admin/teacher/student/parent) via `api/permissions.py` — no new role system.
- **Config** is a single settings package (`smarteducation/settings/`) selecting
  dev/prod by `DJANGO_ENV`, loading `.env` from a pinned path, with `DATABASE_URL`
  as the single DB source and hard startup failure for missing required prod vars.
  See [AUDIT.md](AUDIT.md) §"Phase 1 decisions".

## Frontend (`frontend/`)

- **React + Vite** (chosen for componentized role dashboards; stated up front).
- **JWT** stored in `localStorage`; `api.js` attaches `Authorization: Bearer` and
  auto-refreshes once on 401.
- Talks to the backend **only** through `VITE_API_BASE_URL` — the backend URL is
  never hardcoded in source.
- UI is a faithful port of the old Bootstrap templates: same navy `#001f8f`
  sidebar, top-bar, `stat-card`/`chart-container` components, Chart.js graphs, and
  the same sections per screen. It is functionally equivalent, not a redesign.

## Request flow

1. Frontend `POST /api/auth/login/` → `{access, refresh}`.
2. Frontend `GET /api/me/` with the access token → role → routes to the matching
   dashboard.
3. Each page calls its `/api/…` endpoint(s); the backend enforces role
   permissions and returns JSON (including chart series for the dashboards).

## Deployment (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))

- **Backend**: one EC2 instance running `docker-compose` (gunicorn behind nginx,
  TLS via certbot), Postgres on **RDS** (default) or a container, `.env` injected
  from SSM/Secrets Manager, `migrate` + `seed_demo_data` + `collectstatic` on
  first deploy.
- **Frontend**: static build deployed to Vercel/Netlify with `VITE_API_BASE_URL`
  pointed at the backend; CORS on the backend allows that origin.
