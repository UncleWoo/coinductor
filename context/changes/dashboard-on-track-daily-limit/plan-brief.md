# Dashboard On-Track + Daily Limit — Plan Brief

> Full plan: `context/changes/dashboard-on-track-daily-limit/plan.md`
> Research: `context/changes/dashboard-on-track-daily-limit/research.md`

## What & Why

This plan implements S-01 by converting the home page into an authenticated budget dashboard with pace-aware on-track status, remaining budget, days left, daily limit, and a compact velocity indicator. The goal is to deliver Coinductor’s core behavior loop: actionable daily spending guidance that updates against current-month reality. This is the north-star slice in the roadmap and the core validation of the product hypothesis.

## Starting Point

Auth, routing, and budget domain models already exist, but the current home page is still a placeholder and no dashboard calculation service is implemented. The codebase has the required data model primitives (`Budget`, `Expense`, soft-delete ownership model), yet no month-scoped aggregation or on-track logic is wired into views/templates.

## Desired End State

After implementation, authenticated users land on `/` and immediately see a clear budget-health dashboard for the current month. The dashboard shows pace-aware on-track status, remaining budget, remaining days, and daily limit, plus a mini velocity indicator. Two explicit empty states are supported: no budget configured (setup CTA) and budget configured with no expenses yet (full-allowance guidance).

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
| --- | --- | --- | --- |
| Dashboard scope | Include core metrics plus mini velocity indicator | User explicitly requested pace visualization while keeping chart-free MVP UI | Plan |
| On-track logic | Pace-aware rule (not simple remaining>=0) | Better reflects sustainable spending behavior and product intent | Plan |
| Empty states | Two branches: no-budget CTA + no-expenses guidance | Prevents misleading zero dashboards and gives clear next action | Plan |
| Code structure | Keep `home` FBV, add `budget/services.py` | Matches current routing pattern while isolating business logic for tests | Plan |
| Data filtering | Current month + user-owned + `is_deleted=False` | Aligns with existing model semantics and avoids stale/deleted data pollution | Plan |
| Automated test strategy | Django integration tests as E2E-equivalent for S-01 | Repo has no browser E2E tooling and this keeps scope/time under control | Plan |

## Scope

**In scope:**
- `@login_required` dashboard home route.
- New service-layer monthly calculations and pace-aware status logic.
- Dashboard UI for metrics, status, velocity indicator, and two empty states.
- Unit + integration tests for calculation correctness, auth gating, and render states.

**Out of scope:**
- Browser automation stack (Playwright/Selenium) in this change.
- Charts/analytics libraries or advanced trend visualizations.
- Cross-month carryover budgeting behavior.
- New app split (`dashboard/`) or budget/expense entry feature expansion.

## Architecture / Approach

Home route remains the dashboard entrypoint and delegates metric computation to a new `budget/services.py` module. The service performs month-bounded ORM aggregations for `Budget` and `Expense`, computes remaining budget/daily limit/velocity/on-track, and returns normalized context for `home.html`. The template renders state-driven UI branches (normal, no-budget, no-expenses) with existing Tailwind conventions.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Dashboard Calculation Service | `budget/services.py` + unit tests for monthly metrics and pace-aware status | Edge-case math or inconsistent scope filters can produce misleading dashboard numbers |
| 2. Auth-Protected Dashboard View Wiring | `home` view protected and wired to service output with integration tests | Route/auth regressions could break existing login-to-home flow |
| 3. Dashboard Template UI + States | Full S-01 UI with velocity indicator and explicit empty states | Conditional rendering complexity can create confusing state transitions |
| 4. S-01 End-to-End Verification (Django Stack) | Consolidated Django automated/manual validation of full user flow | “E2E-equivalent” approach may miss true browser-only issues |

**Prerequisites:** F-02 domain models/migrations are present and applied; existing auth flow remains functional.
**Estimated effort:** ~2-3 implementation sessions across 4 phases.

## Open Risks & Assumptions

- Assumes F-02 model layer is fully available and consistent in runtime environments.
- Pace-aware on-track behavior near month start/end needs careful edge handling to avoid surprising status flips.
- True browser automation is deferred, so final confidence still relies on targeted manual checks.

## Success Criteria (Summary)

- Authenticated users see a correct, current-month dashboard with pace-aware on-track status and daily limit.
- Empty states are explicit and actionable (no-budget CTA, no-expenses guidance).
- Automated Django test coverage protects core calculations, auth access, and rendering-state behavior.
