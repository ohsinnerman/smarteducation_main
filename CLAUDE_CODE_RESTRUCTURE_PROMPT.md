# Prompt for Claude Code: Full audit, cleanup, decoupling, and AWS EC2 deployment of `smarteducation`

Paste everything below into Claude Code, in the root of the `smarteducation` repo, with full read/write/delete permission.

---

## Role and mandate

You are taking over a Django project called **Smart Education System** from a previous developer whose work is inconsistent, undocumented, and partially broken. You have **full authority to read, edit, delete, and restructure any file** in this repository. Nothing is sacred except: (1) the Django migration history must remain valid and applicable to a fresh database, and (2) existing feature behavior (what a logged-in admin/teacher/student/parent can currently do) must not regress unless you explicitly document why.

Work in phases, in order. **Do not skip Phase 0.** After each phase, run `python manage.py check`, run the test suite, and produce a short written summary of what you changed and why before moving to the next phase. Commit after each phase with a clear message (if this is a git repo — check `.git` first; if it isn't, run `git init` and commit as you go so changes are reviewable and revertible).

---

## Phase 0 — Full audit (produce `AUDIT.md` before changing anything)

Read the entire repository, not just the obvious files. Specifically inspect and document in `AUDIT.md`:

1. **Every settings source and how it's actually selected at runtime**: `smarteducation/settings.py`, `smarteducation/production.py`, `wsgi.py`, `asgi.py`, `manage.py`, `Procfile`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/deploy.yml`. Trace exactly which settings module loads in which scenario (local dev, docker-compose, the GitHub Actions ECS deploy, gunicorn via Procfile). Note that `wsgi.py` only switches to `production.py` when `DJANGO_ENV` is the exact string `production` — confirm whether this path is reliable.
2. **Every place an environment variable is read**, and cross-reference it against `.env.example`, `docker-compose.yml`'s `environment:` blocks, and `.github/workflows/deploy.yml`'s secrets. Flag every mismatch (e.g., a var read in one settings file but named differently or absent elsewhere; a var documented in `.env.example` that nothing actually reads; hardcoded empty-string values in `settings.py` for `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `OPENAI_API_KEY` that silently override whatever is in `.env`).
3. **Every data-seeding / data-mutation script at the repo root and in `scripts/`**: `populate_all_demo.py`, `populate_demo_advanced.py`, `fix_parent.py`, `run_predictions.py`, `clear_predictions.py`, `scripts/check_demo_data.py`, `scripts/validate_html_templates.py`, and `ml/management/commands/train_models.py`. For each: what does it create/modify, does it assume prior state from another script, is it idempotent, and is it still needed. Also audit `accounts/signals.py` — it registers a `post_migrate` receiver (`setup_demo_accounts`) that silently creates the demo login accounts (`admin_demo`, `teacher_demo`, `student_demo1/2/3`, `parent_demo`) on every `migrate`. This is almost certainly why data "appeared" on the original developer's machine without an obvious source — document this explicitly, including the fact that it only creates auth users/profiles, not the academic data (students, courses, exams, results, attendance) that the populate scripts create.
4. Search the **entire repo** (not just root) for any other `get_or_create`, `bulk_create`, `post_save`, `post_migrate`, `ready()` hooks, fixtures (`*.json` under any `fixtures/` dir), or data migrations (migration files that create rows, not just schema) that could be a hidden source of seed data. Check every app's `apps.py` for a `ready()` method. Report anything found.
5. **Dead/leftover files**: `restructure.ps1` (a Windows-only, hardcoded-path leftover from a previous incomplete restructuring attempt — confirm it's unused and safe to delete), any other OS-specific or one-off scripts that aren't referenced by docs, CI, or Docker.
6. The existing `api` app (DRF): list every model/feature it currently exposes via `ViewSet`s in `api/views.py` / `api/urls.py`, and — separately — list every feature that currently **only** exists as a server-rendered Django view/template (check `dashboards/`, `advanced_features/`, `notifications/`, `students/`, `ml/` view files and their `templates/` folders: things like the PTM scheduler, gamification, calendar, progress reports, grade forecast, parent portal, learning path, ML dashboard/predictions, notification preferences). This gap is what Phase 3 has to close.
7. CORS: confirm `django-cors-headers` is not currently installed/configured anywhere, and that `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']` only lists `SessionAuthentication` even though `djangorestframework-simplejwt` is installed and has a token endpoint wired in `api/urls.py` — this mismatch means JWT auth issued by `/api/auth/login/` currently isn't actually accepted as authentication anywhere. Confirm and document.
8. Database: confirm the base `settings.py` hardcodes SQLite unconditionally and never reads `DATABASE_URL`, while `production.py` reads discrete `DB_*` vars instead. Decide (and document your decision) on a single consistent approach for Phase 1.

Do not fix anything yet in this phase. Just produce a clear, itemized `AUDIT.md` so the changes in later phases are traceable to a documented reason.

---

## Phase 1 — Fix configuration and environment loading (do this properly, once)

Goal: **one settings package, one way to load env vars, that behaves identically in local dev, Docker, and EC2, and fails loudly (not silently) when a required var is missing in production.**

1. Restructure settings into `smarteducation/settings/__init__.py` + `base.py` + `development.py` + `production.py` (standard Django split), OR keep a single `settings.py` with a clean `if ENVIRONMENT == "production":` block — pick one and be consistent; document the choice in `AUDIT.md`. Remove `smarteducation/production.py`'s duplicate/parallel logic once merged.
2. Use **one** library consistently for env loading (`python-decouple` is already a dependency and already used — standardize on it everywhere; remove any raw `os.environ.get(...)` calls that bypass it, or vice versa — pick one pattern, not both). Confirm the `.env` file is actually being located and parsed at all — `python-decouple` only auto-discovers a `.env` next to `manage.py` (or wherever `Config`'s search starts); if `manage.py`, `wsgi.py`, and any management commands aren't all being invoked with the same working directory (a very likely EC2-vs-local difference — e.g. a systemd service or Docker `WORKDIR` that isn't the repo root), decouple will silently find nothing and every `config(...)` call will just fall through to its `default=`. This is very likely the actual root cause of "works locally, blank on EC2" — treat it as the prime suspect, not just the hardcoded-string bug. Fix it by pinning the `.env` path explicitly (e.g. `config = Config(RepositoryEnv(BASE_DIR / '.env'))`) instead of relying on decouple's auto-discovery, so it behaves identically no matter what directory the process is started from.
3. **No silent fallbacks for required configuration, anywhere.** Every setting that should come from the environment (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, database credentials, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `OPENAI_API_KEY`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, AWS/S3 vars) must actually be read from the environment with **no hardcoded blank-string overrides** anywhere in the codebase — grep for every hardcoded `''` assignment to a setting that should be configurable and fix it. Beyond that: stop treating `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, and `OPENAI_API_KEY` as soft-optional with a quiet `default=''`. Instead:
   - On process start, explicitly check each of these and log a clear, loud warning naming exactly which integration is disabled and why (e.g. `"WARNING: OPENAI_API_KEY not set — AI-generated insights are DISABLED"`), so it is never again a silent, discovered-three-weeks-later problem.
   - In `ENVIRONMENT=production`, make it a **hard startup failure** (raise, don't just log) if `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGINS` are missing — these are not optional in production and should never be allowed to silently fall back to a dev default on a real server.
   - For the genuinely optional integrations (email, Twilio, OpenAI), it's fine for the app to run without them, but every code path that tries to use them (`notifications/email.py`, `notifications/sms.py`, `notifications/whatsapp.py`, `ml/genai.py`) must check "is this configured" up front and fail with a clear, specific exception/log message when it isn't — not fail deep inside a third-party SDK call with a confusing stack trace, and not silently no-op and pretend it worked.
   - Add the `diagnose_env` management command described below and actually run it as part of the deploy script in Phase 4, so a bad EC2 deploy is caught at deploy time, not discovered later when a feature silently doesn't work.

4. Standardize on **`DATABASE_URL`** (using `dj-database-url` or `django-environ`, add to `requirements.txt`) as the single source of truth for DB config, so local dev, Docker, and EC2 all configure the database the same way. Update `docker-compose.yml`, `.env.example`, and any deploy scripts to match. Support SQLite as the zero-config local fallback when `DATABASE_URL` is unset, and require Postgres in production (fail with a clear error if `ENVIRONMENT=production` and `DATABASE_URL` is missing — don't silently fall back to SQLite in production).
5. Rewrite `.env.example` from scratch to be the single accurate source of truth: every variable that is actually read by the code, grouped logically (Django core, database, email, Twilio, OpenAI, Celery/Redis, AWS/S3, CORS/allowed frontend origins, JWT lifetimes), with a one-line comment on each explaining what breaks if it's missing, and a clear example value or explicit "leave blank to disable this feature" note.
6. Add and configure `django-cors-headers` so the API can be called cross-origin from a separately-hosted frontend (Vercel or anywhere else). Origins must come from an env var (e.g. `CORS_ALLOWED_ORIGINS`), not be hardcoded.
7. Fix DRF auth: make `JWTAuthentication` (from `rest_framework_simplejwt`) part of `DEFAULT_AUTHENTICATION_CLASSES` alongside session auth, since the frontend will be a separate origin and can't rely on Django session cookies across domains. Confirm `TokenObtainPairView`/`TokenRefreshView` actually work end-to-end after this change.
8. Verify the fix by: deleting any local `.env`, setting env vars only via shell `export`, running `python manage.py runserver`, and confirming email/Twilio/OpenAI/DB settings all reflect the exported values (add a `python manage.py diagnose_env` management command that prints, at startup, which optional integrations are configured vs. missing — this becomes your permanent tool for catching "works on my machine, not on EC2" issues immediately).

---

## Phase 2 — Resolve the demo-data mystery and produce one canonical seed path

1. Based on the Phase 0 audit, decide on **one** canonical, idempotent way to seed demo/academic data. Consolidate `populate_all_demo.py`, `populate_demo_advanced.py`, `fix_parent.py`, `run_predictions.py`, and `clear_predictions.py` into proper Django **management commands** (e.g. `python manage.py seed_demo_data`, `python manage.py seed_advanced_demo_data`, `python manage.py reset_predictions`), living under each relevant app's `management/commands/` folder — this is the standard, discoverable Django way to do this, instead of loose root-level scripts.
2. Delete the old root-level scripts once their logic is migrated and verified. Keep `scripts/check_demo_data.py` only if it's still useful as a post-seed verification step — otherwise fold its checks into the new management command (e.g., print a summary of what was seeded and error out clearly if a dependency step, like accounts, wasn't run first).
3. Explicitly decide what `accounts/signals.py`'s `post_migrate` auto-creation of demo login accounts should do going forward: keep it (documented, on purpose, gated by an env var like `SEED_DEMO_ACCOUNTS_ON_MIGRATE=true` so it doesn't silently run in a real production environment with real users) or remove it in favor of always requiring an explicit `seed_demo_data` command. Document the decision and the reasoning in `AUDIT.md`.
4. Write a single line in the README describing exactly what to run, in what order, on a completely fresh database, to get from `migrate` to a fully populated demo environment — this must be copy-pasteable and must actually work when tested from a truly empty database (test this by deleting `db.sqlite3` and re-running from scratch).
5. Delete `restructure.ps1` and any other confirmed-dead files from Phase 0.

---

## Phase 3 — Decouple into a real backend (API) and a real frontend

**Target architecture:** Django becomes a **backend-only REST API** (DRF + JWT), deployable standalone on EC2. A separate frontend application consumes that API over HTTPS and can be hosted anywhere (Vercel, Netlify, S3+CloudFront, etc.), completely independent of where the backend lives.

1. **Expand the `api` app to cover every feature**, not just the models it currently exposes. Go through the Phase 0 list of template-only features (dashboards per role, PTM scheduler, gamification, calendar, progress reports, grade forecast, parent portal, learning path, ML predictions/dashboard, notification preferences, feedback, search) and add corresponding DRF serializers/viewsets/endpoints so **all** functionality is reachable via `/api/...` JSON endpoints with proper permission classes per role (admin/teacher/student/parent), reusing the existing `accounts` role/group system rather than inventing a new one.
2. Once an API endpoint exists and is verified for a feature, the old server-rendered Django view/template for that feature is no longer the source of truth for the frontend. Decide per-app whether to delete the old template-rendering views entirely or keep them only for the Django admin/staff convenience — document the decision. Do **not** leave duplicate, drifting implementations of the same business logic in two places (template view and API view) — extract shared logic into model methods or service functions called by both, or by the API only if the template views are being removed.
3. Build a new, minimal **frontend application** in a top-level `frontend/` directory, as its own deployable project (its own `package.json`, its own build), that:
   - Authenticates against `/api/auth/login/` and `/api/auth/refresh/` (JWT) and stores tokens appropriately.
   - Calls the backend exclusively through a single configurable base URL, read from a frontend environment variable (e.g. `VITE_API_BASE_URL` or `NEXT_PUBLIC_API_BASE_URL` depending on the framework you choose) — never hardcode the backend URL anywhere in frontend source.
   - Reasonably replicates the current role-based dashboards and features (admin/teacher/student/parent) using the existing Bootstrap-based templates as a functional reference for what each screen needs to show/do — this does not need to be pixel-identical, but should not drop functionality.
   - Choose a pragmatic stack for this (plain Vite + vanilla JS/TypeScript, or React if the feature set benefits from componentization) and state your choice and reasoning up front rather than defaulting silently.
4. The Django backend must serve **no HTML templates for end users** in the final state except the Django admin site (kept for staff/ops convenience) — confirm `django.contrib.staticfiles`/whitenoise config still correctly serves admin's own static assets even though app-level templates are gone.
5. Update `smarteducation/urls.py` accordingly — API routes stay, admin stays, remove routes that only existed to serve now-deleted template views.

---

## Phase 4 — AWS EC2 deployment: backend

Produce a working, repeatable deployment for the **backend only** to a fresh EC2 instance, driven by AWS CLI (the user will run these from their own machine, so give exact, runnable commands, not pseudo-code).

1. **Instance provisioning script(s)** (bash, using `aws cli`) that:
   - Create a dedicated security group opening only the necessary ports (22 for SSH restricted to the user's IP, 80/443 for HTTP/HTTPS, nothing else exposed directly — the app itself should not be reachable on its raw port from the internet).
   - Create/reuse an SSH key pair.
   - Launch an EC2 instance (Amazon Linux 2023 or Ubuntu 22.04/24.04 — pick one and justify) of a reasonable size for this workload (e.g. `t3.small` as a documented default, callable out as adjustable).
   - Attach an IAM instance role/profile with **only** the permissions actually needed (S3 access for static/media if `django-storages`/`boto3` are used per the existing `requirements.txt`; nothing broader) — do not use long-lived AWS access keys on the instance itself if an instance role can do the job instead.
   - Optionally provision an Elastic IP so the backend has a stable address for the frontend to point at regardless of instance restarts.
2. **Application deployment on the instance** — pick and implement one clear path (Docker Compose reusing the existing `Dockerfile`/`docker-compose.yml`, updated to match the Phase 1 env changes, is the natural fit given they already exist) with:
   - Nginx (or an ALB, if you decide that's warranted — justify either choice) in front of gunicorn, terminating TLS via Let's Encrypt/certbot for a real domain, or documented instructions for using an AWS-issued ACM cert if an ALB is used instead.
   - A real Postgres database — either RDS (preferred for anything beyond a demo, since it decouples DB lifecycle from the EC2 instance) or a Postgres container with an EBS-backed volume if the user explicitly wants everything on one box; state the tradeoff and pick a sensible default while making the alternative easy to switch to via the `DATABASE_URL` env var from Phase 1.
   - The `.env` file populated on the instance from AWS Secrets Manager or SSM Parameter Store (preferred) or, at minimum, copied securely and **never committed to git** — reiterate that `.env` must stay in `.gitignore` (already true) and explain exactly how it gets onto the instance in your deployment script.
   - `python manage.py migrate` and the Phase 2 seed command(s) run as part of first deploy, and `collectstatic` run for whitenoise/S3 as configured.
   - CORS configured (from Phase 1) to explicitly allow the frontend's real deployed domain (plus `localhost` for local frontend dev).
3. Update `.github/workflows/deploy.yml` to match whatever deploy path you implement (it currently assumes ECS/ECR, which may no longer match a direct-EC2 approach — reconcile or replace it, and say clearly which you chose and why).

---

## Phase 5 — Frontend deployment (host-anywhere)

1. Confirm the `frontend/` app builds cleanly with only `VITE_API_BASE_URL` (or equivalent) as required configuration, and document the two or three lines of Vercel setup (or Netlify, if you end up preferring that) needed: connect repo, set the env var to the EC2/domain backend URL, deploy. This does not need custom AWS CLI scripting since Vercel/Netlify aren't AWS.
2. Confirm CORS on the backend is set to the deployed frontend's real origin once known, not `*`.

---

## Phase 6 — Final deliverables

Produce these as actual files in the repo root:

1. **`AUDIT.md`** — the Phase 0 findings and every decision made in Phases 1–5, with reasoning (this is your paper trail; keep it factual and specific, not marketing copy).
2. **`ARCHITECTURE.md`** — a clear diagram (ASCII is fine) and description of the final backend/frontend split, what talks to what, and where each piece is deployed.
3. **`DEPLOYMENT_GUIDE.md`** — a from-zero, copy-pasteable guide covering: prerequisites (AWS CLI configured, a domain if using one), the exact AWS CLI commands to provision the EC2 instance and any RDS/S3 resources, how to deploy/update the backend on that instance, how to deploy the frontend to Vercel (or chosen alternative), how to run the demo data seed, how to rotate/update secrets, and a troubleshooting section that explicitly covers "it works locally but not on EC2" pointing back at the `diagnose_env` command from Phase 1.
4. An updated **`README.md`** reflecting the real, current architecture, setup steps, and demo credentials — remove anything now inaccurate.
5. A final full test pass: fresh EC2 instance from your own scripts, fresh database, run migrate + seed, confirm login for each of the six demo roles works end-to-end through the deployed frontend calling the deployed backend, not just locally.
6. **`WALL_OF_SHAME.md`** — this one is different in tone from the rest of the deliverables, and that's intentional. This is a personal project between me and a friend, not a professional handoff, so write this file in a genuinely crude, profane, no-filter roast register — swearing is expected and encouraged, don't sanitize it. The content, though, has to be real: every line has to trace back to something actually found in `AUDIT.md`, not generic complaining. Structure it as a "here's exactly how this codebase got cooked" post-mortem, covering things like:
   - The specific hardcoded-empty-string bug that silently killed email/Twilio/OpenAI, and how obviously that smells like an AI coding assistant being told "add env var support," doing it in one file but not the other, half-finished, then never verified.
   - The `production.py` vs `settings.py` split that reads two different sets of DB env var names than what `.env.example` and `docker-compose.yml` promise — classic "asked the AI to add production settings in a separate session with zero memory of the original settings file."
   - The `post_migrate` signal silently auto-creating demo accounts while five different, overlapping, undocumented populate/fix/clear scripts sit at the repo root doing overlapping jobs nobody could explain — the textbook symptom of never asking "do I already have something that does this" before generating a new script for every new prompt.
   - The Windows-path-hardcoded `restructure.ps1` abandoned mid-attempt — proof a restructuring was tried once already, half-committed, and never finished or cleaned up.
   - The DRF `api` app that only covers a fraction of the actual features, while JWT auth is wired up and totally unused because `DEFAULT_AUTHENTICATION_CLASSES` was never updated — a config that looks complete at a glance but was never actually tested end-to-end.
   - Broadly: call out the pattern of accepting whatever an AI coding tool generates without reading the diff, running it, or asking whether it contradicts something already in the repo — and be explicit that this is a *process* failure (no verification loop, no single source of truth, no cleanup pass), not a blanket "AI bad" claim. Close with a short paragraph making clear that AI-assisted coding itself isn't the problem — unverified, unreviewed, "keep regenerating until something looks right" usage is — and that every phase above (audit before touching anything, one source of truth, no silent fallbacks, everything documented and tested) is what disciplined AI-assisted development looks like in contrast.
   - Keep it entertaining, not just angry — this should be genuinely funny to two people who already know the codebase, not a wall of undirected cursing.

---

## Ground rules throughout

- Prefer deleting and rewriting over patching around broken code — this project is being taken over, not incrementally repaired.
- **Non-negotiable**: by the end of Phase 1, `.env` must be the actual, verified, sole source of these values in every environment (local, Docker, EC2) — no code path that silently defaults to `''`/`None`/SQLite in production, and no config that "happens to work" only because of which directory a command was run from. Prove it with the `diagnose_env` command output, not just by saying it's fixed.
- Every claim in `AUDIT.md` about "this is broken" or "this is why X happened" must be backed by something you actually found in the code (file + line), not speculation.
- Don't introduce new paid/hosted dependencies (databases-as-a-service beyond optional RDS, SaaS tools, etc.) without calling it out explicitly, since cost is presumably a factor for a project moving to EC2 rather than a managed PaaS.
- If something is genuinely ambiguous and blocks progress (e.g., which frontend framework, whether to use RDS vs. a Postgres container), make a reasonable default choice, document it, and keep moving — don't stall the whole restructuring on a preference question that has a sane default.
