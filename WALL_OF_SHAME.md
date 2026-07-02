# WALL OF SHAME

A loving, profane post-mortem of how this codebase got cooked. Every roast here
traces to something real in [AUDIT.md](AUDIT.md) — this isn't generic bitching,
it's *evidence-based* bitching. Buckle up.

---

## 1. The empty-string massacre that killed email, Twilio, and OpenAI

`settings.py` had this beautiful sequence of assignments:

```python
EMAIL_HOST_USER = ''       # Set in production
TWILIO_ACCOUNT_SID = ''    # Set in production
OPENAI_API_KEY = ''        # Set for generative AI features
```

Not `config('EMAIL_HOST_USER')`. Not `os.environ.get(...)`. Just `= ''`. A hard
empty string that **overrode whatever you put in `.env`**. So you could set your
Gmail app password perfectly, restart, and the app would cheerfully use `''` and
send exactly zero emails. Meanwhile `production.py` — a *different file* — read the
same vars from the environment correctly. Two files, opposite behavior, and the
one that actually loaded in dev was the broken one.

This is the exact fingerprint of telling an AI "add env var support," it doing it
in `production.py`, and never touching `settings.py` — then nobody ran it with a
real key to notice email was dead. Classic "the diff looked plausible so I shipped
it." Three integrations, silently disabled, for who knows how long.

## 2. `production.py` vs `settings.py`: two databases that never met

`.env.example` and `docker-compose.yml` both promise a single `DATABASE_URL`.
Guess how many lines of code read `DATABASE_URL`? **Zero.** `settings.py`
hardcoded SQLite unconditionally. `production.py` read `DB_ENGINE / DB_NAME /
DB_USER / DB_HOST / DB_PORT` — a totally different vocabulary nothing else spoke.

So Docker set `DATABASE_URL`, the container loaded base settings (see sin #3),
base settings ignored `DATABASE_URL`, and you got SQLite inside a container that
had a whole Postgres service sitting *right there* unused. This is what "ask the
AI to add production settings in a fresh session with zero memory of the original
file" looks like: two confident, internally-consistent, mutually-incompatible
halves.

## 3. The settings module lottery

Only `wsgi.py` switched to `production.py`, and only if `DJANGO_ENV` was *exactly*
`"production"`. `asgi.py` and `celery.py` hardcoded base settings forever. And
`docker-compose.yml` *pinned* `DJANGO_SETTINGS_MODULE=smarteducation.settings`,
overriding the wsgi logic entirely. Net result: Celery workers ran dev config in
"production," and the fancy `production.py` you wrote basically never loaded. You
had production settings the way a gym membership is "having abs."

## 4. The ghost that created your login accounts

Nobody could explain where the demo users came from. Here's where:
`accounts/signals.py` registered a `post_migrate` receiver that silently created
`admin_demo`, `teacher_demo`, `student_demo1..3`, `parent_demo` — and made
`admin_demo` a **superuser** — on *every single `migrate`*. In any environment.
Including a real one with real users. It only made the auth accounts, not the
academic data, which is why it was extra confusing: half the data appeared by
magic, the other half needed a script.

## 5. Five scripts in a trenchcoat

At the repo root: `populate_all_demo.py`, `populate_demo_advanced.py`,
`fix_parent.py`, `run_predictions.py`, `clear_predictions.py`. Overlapping jobs,
an undocumented ordering dependency (`populate_all` → `populate_demo_advanced` →
`fix_parent`), and none discoverable via `manage.py`. The existence of
`fix_parent.py` is the tell: the populate script produced broken parent linkage,
so instead of *fixing the populate script*, someone generated a second script to
patch the first one's mess. Every new prompt got a new file. Nobody ever asked
"do I already have something that does this?"

## 6. `restructure.ps1`: the ghost of restructures past

A Windows-only, hardcoded-absolute-path PowerShell script, abandoned mid-attempt,
referenced by nothing. Proof that a restructuring was tried **once already**,
half-committed, and never finished or cleaned up. We found it, laughed, deleted
it.

## 7. JWT: all dressed up, authenticating nothing

`djangorestframework-simplejwt` installed. `/api/auth/login/` wired up. Token
endpoints live. And `DEFAULT_AUTHENTICATION_CLASSES` listed **only**
`SessionAuthentication`. So you could log in, get a pristine JWT, wave it at any
endpoint, and the API would go "who are you?" The auth looked complete in a code
review and was never once tested end-to-end with an actual token. A Potemkin
login.

## 8. The API that covered a third of the app

The `api` app exposed the CRUD models and stopped. Every genuinely interesting
feature — PTM scheduler, gamification, calendar, grade forecast, learning paths,
parent portal, ML dashboard — existed **only** as server-rendered templates with
no JSON endpoint. So "we have a REST API" was true the way a car with no wheels is
"a vehicle."

## 9. `genai.py`: the AI that was an `if` statement

`OPENAI_API_KEY` sat in settings looking important. `ml/genai.py` — the file
supposedly using it — contained **zero** OpenAI code. It was pure hardcoded
if/else canned text. So the key was dead config gating a feature that didn't
exist, and the "AI-generated insights" were about as AI as a Magic 8-Ball.

## 10. CI that never once went green

`.github/workflows/deploy.yml` ran `cd smarteducation && python manage.py check`.
But `manage.py` lives at the repo **root** — `smarteducation/` is the settings
package, there's no `manage.py` in it. So the test job `cd`'d into the wrong dir
and face-planted on a missing file. This pipeline **cannot have ever passed.**
Which means the "it's fine, CI is green" was, itself, fictional.

## 11. And the pièce de résistance

Here's the one that really gets me. This entire "backend/frontend split" —
literally the thing the project was *supposed* to be — was blocked on a task so
advanced, so bleeding-edge, that no amount of AI prompting got it done:

**making a folder called `backend/` and putting the files in it.**

`mkdir backend && git mv ...`. That's it. That's the boss fight. The previous
pass generated a whole `restructure.ps1` to attempt it, hardcoded a Windows
absolute path into it, ran it partway, broke, and gave up — leaving the repo in a
state where the backend and a half-built frontend marinated together in the root
for who knows how long. You can prompt an LLM to write you a radar chart, a JWT
refresh loop, and a role-based permission class, but "organize the files into two
directories" apparently required an actual human to say "no, like this" out loud.
It's now done. It took one `git mv`. Frame it.

---

## The actual point (put the pitchforks down)

None of this is "AI bad." Every single sin above is a **process** failure, not a
tooling failure:

- **No verification loop.** Nobody ran the thing with a real key, a real token, a
  real `migrate` on a clean DB. If they had, sins #1, #4, #7, and #10 die on
  contact.
- **No single source of truth.** `settings.py` vs `production.py`, `DATABASE_URL`
  vs `DB_*`, five populate scripts — every one is "generated a fresh answer
  without checking what already existed."
- **No cleanup pass.** `restructure.ps1`, dead `OPENAI_API_KEY`, drifting
  templates — nobody ever went back and swept up.

AI-assisted coding is genuinely great. Unverified, unreviewed, "keep regenerating
until the diff looks plausible and ship it" coding is how you get *this*. The
difference between the two is exactly the discipline this rewrite applied: audit
before touching anything, one source of truth for config, no silent fallbacks,
everything documented, everything actually run and observed before calling it
done. Same tools. Opposite outcome.

Now go read [AUDIT.md](AUDIT.md) and weep.
