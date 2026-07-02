# AUDIT.md — Smart Education System

Phase 0 audit. Every "this is broken" claim below cites a file and line I actually
read. This document is the paper trail; later phases reference these item numbers.

Scope note: the owner chose to execute **Phase 0 + Phase 1 only** in this pass
(config/env layer), with the frontend (Phase 3), seed consolidation (Phase 2), and
EC2/AWS deployment (Phases 4–5) deferred. Decisions for those phases are recorded
here where they affect Phase 1, but the work is not done yet.

---

## 1. Settings sources and how each is selected at runtime

| Entry point | Line | Settings module it selects |
|---|---|---|
| `manage.py` | [manage.py:9](manage.py#L9) | `smarteducation.settings` (unconditional `setdefault`) |
| `smarteducation/wsgi.py` | [wsgi.py:14-16](smarteducation/wsgi.py#L14-L16) | `settings`, then **overridden to** `production` only if `os.environ['DJANGO_ENV'] == 'production'` (exact string) |
| `smarteducation/asgi.py` | [asgi.py:14](smarteducation/asgi.py#L14) | `smarteducation.settings` (never switches to production) |
| `smarteducation/celery.py` | [celery.py:4](smarteducation/celery.py#L4) | `smarteducation.settings` (never switches) |
| `Procfile` | [Procfile:1](Procfile#L1) | gunicorn → `wsgi` → whatever `DJANGO_ENV` is at process start |
| `docker-compose.yml` web/celery | [docker-compose.yml:15](docker-compose.yml#L15), [:44](docker-compose.yml#L44) | forces `DJANGO_SETTINGS_MODULE=smarteducation.settings` (i.e. **never production, even in Docker**) |
| `.github/workflows/deploy.yml` | — | builds a Docker image; container `CMD` runs `wsgi`, so same `DJANGO_ENV` rule |

**Findings:**

- **1a. The production settings path is unreliable and inconsistent.** Only `wsgi.py`
  switches to `production.py`, and only when `DJANGO_ENV` is exactly `"production"`.
  `asgi.py` ([asgi.py:14](smarteducation/asgi.py#L14)) and `celery.py`
  ([celery.py:4](smarteducation/celery.py#L4)) hardcode `smarteducation.settings` and
  will **never** load production settings — so Celery workers and any ASGI server run
  with dev config (SQLite, `DEBUG` default, no whitenoise) regardless of environment.
- **1b. Docker actively pins the wrong module.** `docker-compose.yml`
  ([:15](docker-compose.yml#L15), [:44](docker-compose.yml#L44)) sets
  `DJANGO_SETTINGS_MODULE=smarteducation.settings`, which *overrides* the wsgi
  `DJANGO_ENV` logic. So even in a container that provides `DATABASE_URL`, the base
  `settings.py` is loaded — and base settings never read `DATABASE_URL` (see §8).
- **1c. `manage.py migrate` never uses production settings**, so migrations always
  run against SQLite unless the operator manually exports `DJANGO_SETTINGS_MODULE`.

---

## 2. Environment variables — read sites vs. what is promised

`os.environ` / `config()` read sites: see grep of all `*.py` (§ evidence below).

**2a. Two different env-loading mechanisms, split by file.**
- `settings.py` uses `python-decouple` `config(...)` — but only for
  `DJANGO_ENV`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
  ([settings.py:20-36](smarteducation/settings.py#L20-L36)).
- `production.py` uses raw `os.environ.get(...)` for everything
  ([production.py:7-44](smarteducation/production.py#L7-L44)).
- Result: **inconsistent pattern** the mandate calls out. Standardize on decouple
  (Phase 1).

**2b. Hardcoded blank strings in `settings.py` silently override `.env`.**
[settings.py:183-189](smarteducation/settings.py#L183-L189) and
[settings.py:199](smarteducation/settings.py#L199):
```
EMAIL_HOST_USER = ''          # line 183
EMAIL_HOST_PASSWORD = ''      # line 184
TWILIO_ACCOUNT_SID = ''       # line 187
TWILIO_AUTH_TOKEN = ''        # line 188
TWILIO_PHONE_NUMBER = ''      # line 189
OPENAI_API_KEY = ''           # line 199
```
These are plain literals, **not** `config(...)` calls. In the default (development)
path, they win over anything in `.env`. So a developer who sets `EMAIL_HOST_USER` in
`.env` gets an empty value at runtime. **This is the "email/Twilio silently dead"
bug.** `production.py` *does* read them from env
([production.py:37-42](smarteducation/production.py#L37-L42)) — but per §1, production
settings rarely actually load. So in practice these are always empty.

**2c. DB env-var name mismatch between `production.py` and everything else.**
`production.py` reads discrete `DB_ENGINE / DB_NAME / DB_USER / DB_PASSWORD /
DB_HOST / DB_PORT` ([production.py:11-19](smarteducation/production.py#L11-L19)).
But `.env.example` ([.env.example:15](.env.example#L15)) and `docker-compose.yml`
([:16](docker-compose.yml#L16), [:45](docker-compose.yml#L45)) promise a single
`DATABASE_URL`. **Nothing reads `DATABASE_URL`.** These two vocabularies never meet.

**2d. `REDIS_URL` is passed by Docker but read nowhere.**
`docker-compose.yml` ([:17](docker-compose.yml#L17), [:46](docker-compose.yml#L46))
sets `REDIS_URL`. Settings read `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND`
([settings.py:192-193](smarteducation/settings.py#L192-L193)) as hardcoded
`redis://localhost:6379/0` — never from env, and never `REDIS_URL`. So Celery in
Docker points at `localhost`, not the `redis` service.

**2e. `.env.example` documents AWS keys nothing reads.**
[.env.example:33-36](.env.example#L33-L36) list `AWS_ACCESS_KEY_ID` etc.; no
settings file references them (django-storages/boto3 are installed but never
configured in any settings module).

**2f. `CELERY_BROKER_URL` in `.env.example` isn't read either** —
[.env.example:30](.env.example#L30) sets it, but settings hardcode the value
([settings.py:192](smarteducation/settings.py#L192)).

---

## 3. Data-seeding / mutation scripts

Root-level loose scripts (all bootstrap Django by hand via
`os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')`):

| Script | Purpose (from code) | Idempotent? | Assumes prior state? |
|---|---|---|---|
| `populate_all_demo.py` | creates students/courses/exams/results/attendance via `get_or_create`/`create` | partially | assumes demo auth accounts exist (from signal, §4a) |
| `populate_demo_advanced.py` | advanced features demo data | partially | assumes `populate_all_demo` ran |
| `fix_parent.py` | patches parent↔student linkage after the fact | no (one-off fix) | assumes both above ran |
| `run_predictions.py` | runs ML predictor over students | re-runnable | needs trained model + students |
| `clear_predictions.py` | deletes prediction rows | yes | — |
| `scripts/check_demo_data.py` | read-only verification counts | yes (read-only) | — |
| `scripts/validate_html_templates.py` | template lint helper | yes | — |
| `ml/management/commands/train_models.py` | the one *proper* mgmt command | — | needs data |

**3a.** Five overlapping loose scripts doing overlapping jobs, with an undocumented
ordering dependency (`populate_all` → `populate_demo_advanced` → `fix_parent`), none
discoverable via `manage.py`. `fix_parent.py` existing at all implies the populate
scripts produce broken parent linkage that needs a manual patch — classic "generate a
new script per prompt instead of fixing the first one." (Consolidation is **Phase 2**,
deferred.)

---

## 4. Hidden seed sources (signals, ready(), fixtures, data migrations)

**4a. `post_migrate` auto-creates demo login accounts on EVERY migrate.**
[accounts/signals.py:95-97](accounts/signals.py#L95-L97) registers
`setup_demo_accounts` on `post_migrate`, which calls `ensure_demo_accounts()`
([signals.py:75-92](accounts/signals.py#L75-L92)). This silently creates
`admin_demo / teacher_demo / student_demo1..3 / parent_demo` with fixed passwords
and sets `admin_demo` as **superuser** — on any `migrate`, including production.
Wired via `accounts/apps.py` `ready()`
([accounts/apps.py:8-9](accounts/apps.py#L8-L9)).
**This is why login accounts "appeared" with no obvious source.** Note it only
creates *auth users/profiles*, NOT the academic data (students/courses/exams/results/
attendance) — that still comes from the §3 scripts. (Gating this behind
`SEED_DEMO_ACCOUNTS_ON_MIGRATE` is **Phase 2**, deferred; flagged here as a
production risk.)

**4b. Other hooks found:** `post_save` on `UserProfile` syncs groups
([signals.py:62-72](accounts/signals.py#L62-L72)) — legitimate, keep. No `ready()`
methods other than `accounts/apps.py`. No `fixtures/*.json`. **No data migrations**
(grep for `RunPython`/`bulk_create`/`.create(` in `*/migrations/*.py` returned
nothing). `get_or_create`/`post_save` also appear in `students/views.py` and
`notifications/views.py` (request-time, not seed).

---

## 5. Dead / leftover files

- **5a. `restructure.ps1`** — Windows-only, hardcoded-path leftover from an
  abandoned prior restructuring attempt. Not referenced by any doc, CI, or Docker
  file. Safe to delete (deletion is Phase 2). Its mere existence is evidence a
  restructure was tried once and never finished.

---

## 6. API coverage vs. template-only features

`api/urls.py` exposes ViewSets for: students, courses, subjects, exams, results,
attendance, enrollments, feedback, notifications, notification-preferences,
predictions ([api/urls.py:7-17](api/urls.py#L7-L17)), plus JWT login/refresh, one
`admin_dashboard_api`, and `search_api` ([api/urls.py:21-24](api/urls.py#L21-L24)).

**Template-only (no API equivalent)** — these live only as server-rendered views:
- `dashboards/`: student & teacher dashboards (admin has a partial API)
- `advanced_features/`: calendar, gamification, grade_forecast, learning_path,
  parent_portal, progress_reports, ptm_scheduler (all seven have templates, no API)
- `notifications/`: preferences UI beyond the viewset
- `ml/`: ML dashboard/prediction views + templates

Closing this gap is **Phase 3** (deferred). Recorded so it's traceable.

---

## 7. CORS and DRF/JWT auth mismatch

- **7a. `django-cors-headers` is not installed or configured.** Not in
  `INSTALLED_APPS` ([settings.py:40-61](smarteducation/settings.py#L40-L61)), not in
  `MIDDLEWARE` ([settings.py:62-70](smarteducation/settings.py#L62-L70)), not in
  `requirements.txt`. A separate-origin frontend cannot call the API. (Fixed in
  Phase 1.)
- **7b. JWT is issued but never accepted.**
  `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']` lists **only**
  `SessionAuthentication` ([settings.py:156-158](smarteducation/settings.py#L156-L158)),
  yet `TokenObtainPairView`/`TokenRefreshView` are wired at
  [api/urls.py:21-22](api/urls.py#L21-L22) and `simplejwt` is installed
  ([settings.py:50](smarteducation/settings.py#L50)). A token from `/api/auth/login/`
  authenticates **nothing** — it's dead config that *looks* complete. (Fixed in
  Phase 1.)

---

## 8. Database configuration

- **8a.** Base `settings.py` hardcodes SQLite unconditionally
  ([settings.py:96-101](smarteducation/settings.py#L96-L101)) and **never reads
  `DATABASE_URL`**.
- **8b.** `production.py` reads discrete `DB_*` vars
  ([production.py:11-19](smarteducation/production.py#L11-L19)) — a different scheme
  from `.env.example`/compose (§2c).
- **Decision (Phase 1):** standardize on a single **`DATABASE_URL`** via
  `dj-database-url`. SQLite is the zero-config local fallback when `DATABASE_URL` is
  unset; in `DJANGO_ENV=production` a missing `DATABASE_URL` is a **hard failure**
  (no silent SQLite in prod).

---

## 9. Additional findings (beyond the mandate's checklist)

- **9a. CI is broken: `manage.py` is not where the workflow looks.** `manage.py` is
  at the **repo root**, but `.github/workflows/deploy.yml`
  ([deploy.yml:18-23](.github/workflows/deploy.yml#L18-L23), [:48-49](.github/workflows/deploy.yml#L48-L49))
  runs `cd smarteducation && python manage.py check` / `docker build`. There is no
  `smarteducation/manage.py` or `smarteducation/requirements.txt` — that dir is the
  Django *project package*. So the "test" job's `manage.py check` and the `docker
  build` both fail on `cd` or missing files. The pipeline cannot have been run green.
- **9b. `ml/genai.py` contains no OpenAI code at all.** It is *entirely* the
  fallback path ([ml/genai.py:1-48](ml/genai.py#L1-L48)); `OPENAI_API_KEY` is read
  nowhere in it. So the "AI insights" feature is hardcoded canned text regardless of
  key. The `OPENAI_API_KEY` setting (§2b) is read by nothing — pure dead config.
- **9c. Notification helpers swallow all errors.**
  `send_email_notification` ([notifications/email.py:9-33](notifications/email.py#L9-L33))
  uses `fail_silently=False` but wraps it in a bare `except Exception` that records a
  `status='failed'` Notification and returns `False` — so a misconfigured SMTP looks
  like a normal "failed to send," not a config error. `send_sms_notification`
  ([notifications/sms.py:7-50](notifications/sms.py#L7-L50)) does the same and, when
  Twilio creds are blank, records `failed` and returns `False` silently. Phase 1 adds
  up-front "is this configured" checks + loud logging so a *config* problem is
  distinguishable from a *delivery* problem.
- **9d. `Dockerfile` runs `migrate` in `CMD`** ([Dockerfile:27](Dockerfile#L27)) —
  which, combined with §4a, means every container start silently re-seeds demo
  accounts. Also `collectstatic ... || true` ([Dockerfile:22](Dockerfile#L22))
  swallows static-collection failures.

---

## Phase 1 decisions (summary)

1. **Settings layout:** split into `smarteducation/settings/{__init__,base,development,production}.py`. Delete `smarteducation/production.py`. `__init__` selects dev/prod by `DJANGO_ENV`.
2. **Env loading:** standardize on `python-decouple` with an **explicitly pinned** `.env` path (`Config(RepositoryEnv(BASE_DIR / '.env'))`) so it behaves identically regardless of working directory. Remove all raw `os.environ.get` from settings.
3. **No silent fallbacks:** remove the hardcoded `''` overrides (§2b). Optional integrations (email/Twilio/OpenAI) log a loud, specific warning when unset; required prod vars (`DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`) raise on startup in production.
4. **Database:** single `DATABASE_URL` via `dj-database-url`; SQLite fallback in dev only.
5. **CORS:** add `django-cors-headers`, origins from `CORS_ALLOWED_ORIGINS`.
6. **DRF auth:** add `JWTAuthentication` alongside `SessionAuthentication`.
7. **`diagnose_env` management command** prints configured/missing integrations; run in deploy.
8. **Fix the fan-out:** `asgi.py`, `celery.py`, `docker-compose.yml`, `Procfile`, CI all point at the new settings package consistently; fix the CI `cd smarteducation` path bug (§9a).
9. Optional-integration code paths (`email.py`, `sms.py`, `whatsapp.py`, `ml/genai.py`) get up-front config checks (§9c).

Deferred to later phases: script consolidation & signal gating (Phase 2), API expansion + frontend (Phase 3), EC2/RDS/AWS scripts (Phases 4–5), and the remaining deliverable docs (ARCHITECTURE, DEPLOYMENT_GUIDE, WALL_OF_SHAME).
