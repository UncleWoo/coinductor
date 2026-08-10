# Coinductor — Copilot Instructions

A personal budget tracking web app that shows a dynamic daily spending limit (`remaining_money / remaining_days`).

## Business Logic

The core differentiator: **daily limit = remaining_budget / remaining_days_in_month**

- User defines monthly budget per category (e.g., food: 2000, transport: 500)
- After each expense, recalculate the daily limit
- Dashboard shows: on-track status (yes/no), remaining budget, daily limit

## Conventions

- Keep expense entry to ≤3 taps/clicks from dashboard (per PRD guardrail)
- Use `django.contrib.auth` for email/password authentication
- Single-user model: one account = one budget, no sharing features

## Key Files

- `@context/foundation/prd.md` — Product requirements (budget categories, expense tracking, daily limit calculation)
- `@context/foundation/tech-stack.md` — Stack decisions and rationale
- `@coinductor/settings.py` — Django configuration

## Architecture

- **Stack**: Django 6.0.6, Python 3.13, SQLite (dev), uv for package management
- **Project root**: `coinductor/` contains Django settings, urls, wsgi/asgi

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test <app_name>

# Run a single test
python manage.py test <app_name>.tests.TestClassName.test_method_name

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Install new dependencies (uses uv)
uv pip install <package>
```

<!-- BEGIN @przeprogramowani/10x-cli -->

## 10xDevs AI Toolkit - Module 3, Lesson 4 (E2E Tests)

**For E2E tests, use the `/10x-e2e` skill.** It is the single source of truth
for the workflow — risk → seed test + rules → generate → review against the five
anti-patterns → re-prompt → verify. The skill's `references/` carry the full
rules, anti-patterns, seed pattern, and prompt-template.

A few hard rules that hold even before you invoke the skill:

- **Locators:** `getByRole` / `getByLabel` / `getByText` first; `getByTestId`
  only when accessibility attributes are ambiguous. Never CSS selectors, XPath,
  or DOM structure.
- **Never `page.waitForTimeout()`.** Wait for state: `toBeVisible()`,
  `waitForURL()`, `waitForResponse()`.
- **Test independence + cleanup.** Each test runs standalone — its own setup,
  action, assertion, and cleanup; unique ids (timestamp suffix) so parallel runs
  and re-runs don't collide.

Two boundaries to keep straight:

- **DOM (snapshot) is the default.** Vision (`--caps=vision`) is a supplement for
  visual-only risks (layout, z-index, animation); for pixel regression prefer
  deterministic tools (`toMatchSnapshot`, Argos, Lost Pixel). VLM model
  selection/cost is a debugging topic (Lesson 5), not testing.
- **Healer helps on selectors, harms on logic.** A changed selector → healer
  re-finds it (route through PR review). A changed business behavior → healer
  masks the bug; that failing-test-to-fix case is Lesson 5.

<!-- END @przeprogramowani/10x-cli -->
