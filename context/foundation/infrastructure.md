---
project: coinductor
researched_at: 2026-06-15
recommended_platform: Railway
runner_up: Fly.io
context_type: mvp
tech_stack:
  language: Python
  framework: Django 6.0
  runtime: Python 3.13
---

## Recommendation

**Deploy on Railway.**

Railway offers the best cost-to-value ratio for this Django MVP: $5/month Hobby tier with $5 included credit means low-traffic development is effectively free. Python 3.13 is the default runtime, Django is auto-detected via `manage.py`, and Railpack handles the build/deploy pipeline without Dockerfile configuration. The GA MCP server enables agent-driven operations, and co-located PostgreSQL/Redis templates simplify the data layer. The key tradeoff — unmanaged databases requiring manual backup configuration — is acceptable for an MVP with a solo developer who will configure backups explicitly.

## Platform Comparison

### Scoring Matrix

| Platform | CLI-first | Managed | Agent docs | Stable deploy | MCP | Total | Cost estimate |
|----------|-----------|---------|------------|---------------|-----|-------|---------------|
| **Railway** | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | 5/5 | ~$5/mo |
| **Fly.io** | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | ⚠️ Partial | 4.5/5 | ~$3-6/mo |
| **Render** | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | 5/5 | ~$14/mo |
| **Vercel** | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | ✅ Pass | 5/5 | Free tier |
| ~~Netlify~~ | — | — | — | — | — | — | Dropped: no Python |
| ~~Cloudflare~~ | — | — | — | — | — | — | Dropped: no Django |

### Hard Filters Applied

- **Netlify**: Dropped — no Python runtime for serverless functions; cannot run Django backend
- **Cloudflare Workers**: Dropped — Python Workers (beta) use Pyodide which doesn't support Django's WSGI/ASGI model
- **Vercel**: Kept but deprioritized — Django 6.0 explicitly untested in official examples; serverless cold starts add latency
- **Render**: Kept — solid Django support but $14/mo minimum (web + database) exceeds cost target

### Shortlisted Platforms

#### 1. Railway (Recommended)

**Why it won:** Best alignment with the "minimize cost" constraint while maintaining full Django compatibility. Python 3.13 is the default runtime (no configuration needed for your tech stack). Railpack auto-detects Django projects and runs migrations + Gunicorn automatically. The $5/mo Hobby tier with $5 included usage credit means a low-traffic MVP can run at near-zero cost during development. The CLI (`railway up`, `railway logs`) covers the full deploy/debug loop, and the GA MCP server enables agent-driven operations without experimental flags.

**Key strengths:**
- Python 3.13 default, Django auto-detection
- $5/mo with $5 credit included (effectively free at low traffic)
- Co-located PostgreSQL, Redis, MySQL templates
- GA MCP server with Claude Code, Cursor, Copilot integration
- `llms.txt` documentation for agent consumption

**Tradeoffs accepted:**
- Databases are unmanaged (manual backup configuration required)
- 24-hour image retention on Hobby tier
- Remote MCP marked "work in progress"

#### 2. Fly.io

**Why it scored second:** Container-based flexibility means any Python/Django version works via custom Dockerfile. Explicit Django first-class support with `fly launch` auto-detection. Pricing (~$3-6/mo for minimal app) is competitive, but the lack of a permanent free tier (7-day/2-hour trial only) and experimental MCP server reduce its edge over Railway for cost-conscious MVP development.

**Key strengths:**
- Full container flexibility (any runtime/version)
- Django first-class support in docs
- WebSocket support (if needed later)
- `llms.txt` documentation

**Gaps vs Railway:**
- No permanent free tier (trial expires quickly)
- MCP server explicitly marked "[experimental]"
- No single `rollback` CLI command

#### 3. Render

**Why it scored third:** Mature Django deployment with Python 3.14 default, solid documentation, and GA MCP server. However, the minimum viable cost ($7/mo web service + $7/mo PostgreSQL = $14/mo) exceeds both Railway and Fly.io for equivalent functionality. The free tier's 30-day database expiration and 15-minute spin-down make it unsuitable for anything beyond quick experiments.

**Key strengths:**
- Python 3.14 default (ahead of requirements)
- Mature Django deployment guide
- GA MCP server

**Gaps vs Railway:**
- Higher minimum cost ($14/mo vs $5/mo)
- Free tier database expires after 30 days
- Free tier web services spin down after 15 minutes of inactivity

## Anti-Bias Cross-Check: Railway

### Devil's Advocate — Weaknesses

1. **Databases are unmanaged** — Railway's PostgreSQL templates require you to handle backups, failover, and disaster recovery yourself. A hardware failure without manual backup configuration means data loss.

2. **No rollback CLI command** — Rollbacks happen via dashboard "Redeploy" on historical deployments, not a single `railway rollback` command. This requires navigating deployment history.

3. **Image retention limits** — Hobby plan retains images for only 24 hours. If you discover a bug 2 days later, the previous known-good image may be gone.

4. **Peak-hour deployment restrictions on free/trial** — During high-load periods, free tier users cannot deploy. Debugging production at a bad time means being blocked.

5. **Migration failures have no rollback** — Railpack auto-runs `migrate` but if migrations fail or corrupt data, there's no built-in recovery mechanism.

### Pre-Mortem — How This Could Fail

The team launched Coinductor on Railway Hobby tier, enjoying the $5/mo simplicity. For the first month, everything worked. Then the PostgreSQL instance experienced a disk failure. Because Railway's databases are unmanaged and the team hadn't configured external backups, all user budget data was lost — months of expense entries, gone.

Attempting to restore from a previous deployment failed because the 24-hour image retention had already purged the working version. The team scrambled to redeploy from Git, but the database was empty.

Users abandoned the app. The developer realized too late that "co-located managed services" didn't mean "managed backups." The $5/mo savings didn't account for the cost of rebuilding trust and data. The lesson: Railway is excellent for stateless services but requires explicit backup automation for anything with persistent data.

### Unknown Unknowns

1. **Remote MCP is "work in progress"** — The `railway-agent` tool for multi-step debugging only works with remote MCP, which Railway explicitly marks as incomplete. Agent workflows may hit unexpected limitations.

2. **Railpack replaced Nixpacks recently** — Documentation may reference Nixpacks patterns that no longer apply. Build behavior could differ from older tutorials.

3. **No explicit Django 6.0 testing** — Railway docs mention Django detection but don't confirm Django 6.0 compatibility. Edge cases in newer Django versions may surface unexpected build failures.

4. **Egress costs at scale** — At $0.05/GB, a media-heavy app could see surprise bills. Budget apps with receipt images or exports could hit this.

5. **Network verification requirements** — Unverified accounts on free/trial have network egress restrictions. If your AI insight feature calls external APIs, you may hit blocks until verification completes.

## Operational Story

- **Preview deploys**: Railway auto-deploys on Git push. PR environments require manual setup via Railway Environments feature or GitHub Actions integration. No built-in PR preview URLs like Vercel/Netlify.

- **Secrets**: Environment variables set via `railway variables set KEY=value` or dashboard. Variables are scoped to environment (production/staging). No automatic rotation; manual update required. Access controlled by Railway team permissions.

- **Rollback**: Via dashboard: Deployments → select historical deployment → "Redeploy". No single CLI command. Image retention: 24h (Hobby), 168h (Pro). After retention window, redeploy from Git.

- **Approval**: All deploys are automatic on Git push (no approval gate by default). Production protection requires Pro plan + manual environment configuration. Database deletion requires dashboard confirmation. Secret rotation is human-only.

- **Logs**: `railway logs` streams live logs. `railway logs --build` shows build output. Dashboard provides searchable log history. No MCP tool for log analysis yet (remote MCP is WIP).

## Risk Register

| Risk | Source | Likelihood | Impact | Mitigation |
|------|--------|------------|--------|------------|
| Data loss from unmanaged PostgreSQL failure | Devil's advocate | Medium | High | Configure daily backups to S3/R2 via pg_dump cron job or Railway Volumes snapshot |
| Rollback blocked by 24h image retention | Devil's advocate | Low | Medium | Pin deployments to Git tags; redeploy from known-good commit if image expired |
| Django 6.0 build failure due to untested compatibility | Unknown unknowns | Low | Medium | Test build locally with Railpack before first deploy; have Dockerfile fallback ready |
| Migration corrupts data with no recovery | Devil's advocate | Low | High | Run migrations manually via `railway run` in staging first; maintain migration rollback scripts |
| Peak-hour deployment block during incident | Devil's advocate | Low | Medium | Upgrade to Hobby ($5/mo) immediately; avoid free tier for anything production-facing |
| Egress costs spike from AI feature API calls | Unknown unknowns | Low | Low | Monitor bandwidth in Railway dashboard; set billing alerts |
| Network restrictions block external API calls | Unknown unknowns | Medium | Medium | Complete account verification before deploying AI insight feature |

## Getting Started

1. **Install Railway CLI:**
   ```bash
   curl -fsSL https://railway.com/install.sh | sh
   railway login
   ```

2. **Initialize project:**
   ```bash
   cd /Users/qi03hd/10xDevs
   railway init
   # Select "Empty Project" or link to existing project
   ```

3. **Add PostgreSQL:**
   ```bash
   railway add --database postgres
   # Or via dashboard: New → Database → PostgreSQL
   ```

4. **Configure environment variables:**
   ```bash
   railway variables set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
   railway variables set DEBUG=False
   railway variables set ALLOWED_HOSTS=".railway.app"
   ```

5. **Deploy:**
   ```bash
   railway up
   # Railpack auto-detects Django, runs migrate, starts Gunicorn
   ```

6. **Configure backups (critical — see Risk Register):**
   ```bash
   # Add a cron service or use Railway's scheduled tasks to run:
   # pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d).sql.gz
   # Upload to S3/R2/Tigris
   ```

## Out of Scope

The following were not evaluated in this research:
- Docker image configuration
- CI/CD pipeline setup (GitHub Actions integration exists but not evaluated)
- Production-scale architecture (multi-region, HA, DR)
- Managed backup solutions (third-party services like Supabase, PlanetScale)
- Cost optimization beyond MVP (~$5-20/mo range)
