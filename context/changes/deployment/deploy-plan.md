# Deployment Plan: Coinductor to Railway

---
project: coinductor
platform: Railway
created: 2026-06-17
status: pending
---

## Prerequisites

### Required Before Starting

| Prerequisite | Status | Notes |
|-------------|--------|-------|
| GitHub account | ⬜ | Required for Railway sign-up and auto-deploy |
| Git repository initialized | ⬜ | `git init` if not already done |
| Code pushed to GitHub | ⬜ | Railway will deploy from GitHub repo |
| Python 3.13 installed locally | ⬜ | For testing before deploy |
| Working Django app locally | ⬜ | `python manage.py runserver` works |
| Payment method (optional) | ⬜ | Not required for Hobby tier with $5 credit |

### Environment Verification

Before proceeding, verify:

```bash
# Check Python version
python --version  # Should be 3.13.x

# Check Django works locally
cd /Users/qi03hd/10xDevs
source .venv/bin/activate
python manage.py check  # Should report no issues

# Verify Git is initialized
git status  # Should not error
```

### Accounts Needed

1. **GitHub** — https://github.com (if not already)
2. **Railway** — https://railway.app (sign up with GitHub recommended)

---

## Problem Statement

Deploy the Coinductor Django 6.0 application to Railway with PostgreSQL database, auto-deploy on push to master, and proper production configuration.

## Current State

- Django 6.0.6 project with default development settings
- SQLite database locally, needs PostgreSQL for production
- No `requirements.txt` (using uv/pip freeze)
- No production-ready settings (hardcoded SECRET_KEY, DEBUG=True, empty ALLOWED_HOSTS)
- No Procfile or runtime configuration

## Approach

Prepare the Django project for Railway deployment, then execute the Railway setup. Railway's Railpack will auto-detect Django and handle most configuration, but we need to:

1. Make settings production-ready (env vars for secrets)
2. Generate requirements.txt for Railway
3. Add Gunicorn and psycopg2 dependencies
4. Configure static files for production
5. Set up Railway with PostgreSQL
6. Configure environment variables
7. Link GitHub repo for auto-deploy on master

---

## Todos

### Phase 1: Prepare Django for Production

#### prepare-settings
**Creating production-ready settings.py**

Modify `coinductor/settings.py` to:
- Read SECRET_KEY from environment variable
- Read DEBUG from environment variable (default False)
- Read ALLOWED_HOSTS from environment variable
- Read DATABASE_URL from environment variable (dj-database-url)
- Add WhiteNoise for static files
- Set STATIC_ROOT for collectstatic

#### add-dependencies
**Adding production dependencies**

Install and add to requirements:
- `gunicorn` - WSGI server
- `psycopg2-binary` - PostgreSQL adapter
- `dj-database-url` - Parse DATABASE_URL
- `whitenoise` - Static file serving

#### generate-requirements
**Generating requirements.txt**

Create `requirements.txt` from current environment for Railway to use.

#### add-procfile
**Adding Procfile for Railway**

Create `Procfile` with:
```
web: gunicorn coinductor.wsgi
release: python manage.py migrate
```

---

### Phase 2: Railway Setup (Manual Steps)

#### create-railway-account
**Creating Railway account** [MANUAL]

1. Go to https://railway.app
2. Sign up with GitHub (recommended for auto-deploy)
3. Verify email

#### install-railway-cli
**Installing Railway CLI**

```bash
curl -fsSL https://railway.com/install.sh | sh
railway login
```

#### init-railway-project
**Initializing Railway project**

```bash
railway init
# Select "Empty Project"
```

#### add-postgres
**Adding PostgreSQL database**

```bash
railway add --database postgres
```

---

### Phase 3: Configure & Deploy

#### set-env-vars
**Setting environment variables**

```bash
railway variables set SECRET_KEY="<generated-key>"
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=".railway.app"
```

#### link-github
**Linking GitHub repository for auto-deploy** [MANUAL]

1. Railway Dashboard → Project → Settings
2. Connect GitHub repository
3. Set deploy branch to `master`
4. Enable auto-deploy

#### first-deploy
**Executing first deployment**

```bash
railway up
```

Railpack will:
- Detect Django via manage.py
- Install dependencies from requirements.txt
- Run `python manage.py collectstatic`
- Run `python manage.py migrate` (from Procfile release)
- Start Gunicorn

#### verify-deployment
**Verifying deployment**

1. Check Railway logs: `railway logs`
2. Access deployed URL
3. Verify database connection

---

## Dependencies

```
generate-requirements → prepare-settings
add-procfile → add-dependencies
init-railway-project → install-railway-cli, create-railway-account
set-env-vars → init-railway-project, add-postgres
first-deploy → set-env-vars, link-github, add-procfile, generate-requirements
verify-deployment → first-deploy
```

---

## Risk Mitigations (from infrastructure.md)

| Risk | Mitigation in this plan |
|------|------------------------|
| Data loss from unmanaged PostgreSQL | Configure daily backup after MVP works |
| Django 6.0 build failure | Test build locally first; have Dockerfile fallback |
| Migration corruption | Run migrations manually in staging first |

---

## Out of Scope

- Backup configuration (follow-up task)
- Custom domain setup
- CI/CD pipeline with GitHub Actions (auto-deploy covers MVP)
- Multi-environment (staging/production split)

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `coinductor/settings.py` | Modify for production |
| `requirements.txt` | Create |
| `Procfile` | Create |
