---
project: Coinductor
version: 1
status: draft
created: 2026-06-18
updated: 2026-06-18
prd_version: 1
main_goal: speed
top_blocker: time
---

# Roadmap: Coinductor

> Derived from `context/foundation/prd.md` (v1) + auto-researched codebase baseline.
> Edit-in-place; archive when superseded.
> Slices below are listed in dependency order. The "At a glance" table is the index.

## Vision recap

Users don't stick to budgets because they lack daily feedback — they discover overspend at month-end when it's too late. Coinductor's insight: the "X zł per day" mental model creates a daily feedback loop that changes behavior. Users know exactly how much they can spend today, recalculated after every expense. This is not a generic expense tracker — it's a rebalancing engine that tells you your sustainable daily limit.

## North star

**S-01: User can see on-track status + daily limit** — this is the core product hypothesis from PRD §Vision. If the "X zł dziennie" mental model doesn't change user behavior, nothing else matters. It's the validation milestone — the smallest end-to-end slice (north star) whose successful delivery proves the product makes sense. Sequenced as early as Prerequisites allow.

## At a glance

| ID | Change ID | Outcome (user can …) | Prerequisites | PRD refs | Status |
|---|---|---|---|---|---|
| F-01 | minimal-auth-scaffold | (foundation) Django built-in auth configured; users can sign up and log in | — | FR-001, FR-002 | proposed |
| F-02 | domain-models-migrations | (foundation) Budget, Expense models defined with ORM relationships; migrations applied | — | FR-003, FR-004 | proposed |
| S-01 | dashboard-on-track-daily-limit | see dashboard with on-track yes/no, remaining budget, days left, daily limit | F-01, F-02 | US-01, FR-005, FR-006, FR-007 | proposed |
| S-02 | add-expense-three-taps | add expense (amount, category, date) from dashboard; limit recalculates instantly | S-01 | FR-004, NFR ≤3 taps | proposed |
| S-03 | define-monthly-budget-categories | define monthly budget per category (e.g., food: 2000, transport: 500) | F-02 | FR-003 | proposed |

## Streams

Navigation aid — groups items that share a Prerequisites chain. Canonical ordering still lives in the dependency graph below; this table is the proposed reading order across parallel tracks.

| Stream | Theme | Chain | Note |
|---|---|---|---|
| A | Core rebalancing flow | `F-01` → `F-02` → `S-01` → `S-02` | Must-have path; main_goal=speed prioritizes this strict sequence |
| B | Budget setup | `F-02` → `S-03` | Joins Stream A at `S-01` (S-03 parallel with S-02) |

## Baseline

What's already in place in the codebase as of 2026-06-18 (auto-researched + user-confirmed).
Foundations below assume these are present and do NOT re-scaffold them.

- **Frontend:** partial — Django templates configured (settings.py:57-70), but no actual HTML templates or views exist yet; only a plain-text home view
- **Backend / API:** present — Django framework with WSGI/ASGI entrypoints, basic URL routing (coinductor/urls.py)
- **Data:** partial — Django ORM configured with SQLite, but no custom models, migrations, or domain logic
- **Auth:** absent — Django auth middleware present but no signup/login views, no custom auth layer
- **Deploy / infra:** present — Railway chosen as platform (infrastructure.md), Procfile for deployment
- **Observability:** absent — no logging config, no error tracking, no metrics instrumentation

## Foundations

### F-01: Minimal auth scaffold

- **Outcome:** (foundation) Django built-in auth configured; users can sign up (email+password) and log in via admin or basic views
- **Change ID:** minimal-auth-scaffold
- **PRD refs:** FR-001 (sign up with email+password), FR-002 (log in), §Access Control ("Login with email + password")
- **Unlocks:** S-01 (dashboard requires authenticated user context to show "their" budget)
- **Prerequisites:** —
- **Parallel with:** F-02
- **Blockers:** —
- **Unknowns:** —
- **Risk:** Sequenced first because S-01 (north star) cannot exist without user context. Django's django.contrib.auth handles this out-of-the-box — no custom token logic needed for MVP. If this scaffold proves insufficient (e.g., session handling on Railway), it adds replanning cost, but the baseline shows Django auth middleware is already configured, reducing that risk.
- **Status:** proposed

### F-02: Domain models + migrations

- **Outcome:** (foundation) Budget category, Expense models defined with ORM relationships; migrations applied; data layer ready for business logic
- **Change ID:** domain-models-migrations
- **PRD refs:** FR-003 (budget categories), FR-004 (expenses), §Business Logic ("Monthly budget per category, logged expenses")
- **Unlocks:** S-01 (dashboard queries Budget/Expense), S-02 (adds Expense), S-03 (sets Budget)
- **Prerequisites:** —
- **Parallel with:** F-01
- **Blockers:** —
- **Unknowns:** —
- **Risk:** This is the "invest deeply in data" decision from Step 5. Rebalancing logic (FR-006: remaining_money / remaining_days) requires correct Budget/Expense schema from the start. If the schema is wrong (e.g., missing a category-to-budget relationship, or Expense.date not indexed), S-01 becomes unplannable. Sequenced as foundation so all vertical slices share the same domain model — no schema drift.
- **Status:** proposed

## Slices

### S-01: User can see on-track status + daily limit

- **Outcome:** User can see dashboard with: on-track yes/no (green/red or similar), remaining budget, days left in month, daily limit calculated as remaining_money / remaining_days
- **Change ID:** dashboard-on-track-daily-limit
- **PRD refs:** US-01 (Given user with budget + expenses, When they open dashboard, Then they see on-track answer + daily limit), FR-005 (view budget state), FR-006 (dynamic daily limit), FR-007 (dashboard showing on-track status, remaining budget, daily limit)
- **Prerequisites:** F-01 (auth — dashboard must show data for authenticated user), F-02 (models — dashboard queries Budget/Expense to calculate limit)
- **Parallel with:** —
- **Blockers:** —
- **Unknowns:** —
- **Risk:** This is the north star — if the "X zł dziennie" mental model doesn't resonate with users, the product fails. Sequenced as early as Prerequisites allow (after F-01 + F-02) because everything else (S-02 expense entry, S-03 budget setup) only matters if this core flow works. The calculation (remaining / days_left) is simple, but "remaining" spans all categories — if the query is slow or the UX is unclear, users abandon. PRD §Success Criteria guardrail: "≤3 taps from main screen" implies the dashboard IS the main screen, so this slice must also handle the empty state ("no expenses yet" guidance per US-01 AC).
- **Status:** proposed

### S-02: User can add an expense (≤3 taps)

- **Outcome:** User can add expense (amount, category, date) from dashboard; daily limit recalculates instantly and on-track status updates
- **Change ID:** add-expense-three-taps
- **PRD refs:** FR-004 (add expense with amount, category, date), NFR "Expense entry completes in ≤3 taps/clicks from main screen", US-01 AC "Daily limit recalculates correctly after each new expense"
- **Prerequisites:** S-01 (dashboard must exist to show the recalculated limit; otherwise user has no feedback loop)
- **Parallel with:** S-03
- **Blockers:** —
- **Unknowns:**
  - How should the "≤3 taps" UX look on mobile web? (e.g., inline form vs modal vs quick-add bar) — Owner: designer or solo dev. Block: no (can be prototyped in `/10x-plan`).
- **Risk:** The ≤3 taps guardrail is load-bearing per PRD §Success Criteria — if entry is tedious, users abandon. Sequenced after S-01 (not parallel) because the rebalancing feedback loop (updated daily limit) is what makes expense entry meaningful. If S-01's UX is broken, fixing S-02's form won't save the product. The "recalculates instantly" AC means the view must re-query or the business logic must return the new limit on POST — if that's slow, the feedback loop breaks.
- **Status:** proposed

### S-03: User can define monthly budget categories

- **Outcome:** User can set monthly budget per category (e.g., food: 2000, transport: 500); categories are persisted and used by S-01's daily limit calculation
- **Change ID:** define-monthly-budget-categories
- **PRD refs:** FR-003 (define monthly budget categories), §Business Logic ("Monthly budget per category")
- **Prerequisites:** F-02 (Budget model must exist to persist category limits)
- **Parallel with:** S-02 (both consume F-02, neither blocks the other; S-03 sets budgets, S-02 logs expenses against those budgets)
- **Blockers:** —
- **Unknowns:**
  - Should categories be predefined (fixed list) or user-defined (custom strings)? — Owner: product. Block: no (PRD FR-003 Socrates note says "predefined categories are simpler", so default to fixed list; can be loosened in `/10x-plan`).
- **Risk:** Sequenced in parallel with S-02 because both are inputs to S-01's calculation but neither blocks the other. If budget setup is tedious (many fields, no sensible defaults), users never reach S-01. PRD §Non-Goals says "No advanced settings / customization — sensible defaults only", so this slice must provide a fast onboarding (e.g., common categories pre-filled with zero amounts, user edits only what they need).
- **Status:** proposed

## Backlog Handoff

| Roadmap ID | Change ID | Suggested issue title | Ready for `/10x-plan` | Notes |
|---|---|---|---|---|
| F-01 | minimal-auth-scaffold | Minimal auth scaffold: Django signup + login | yes | Run `/10x-plan minimal-auth-scaffold` |
| F-02 | domain-models-migrations | Domain models + migrations: Budget, Expense schema | yes | Run `/10x-plan domain-models-migrations` |
| S-01 | dashboard-on-track-daily-limit | Dashboard: on-track status + daily limit (US-01) | no | Blocked by F-01, F-02 |
| S-02 | add-expense-three-taps | Add expense in ≤3 taps with instant recalc | no | Blocked by S-01 |
| S-03 | define-monthly-budget-categories | Define monthly budget per category | no | Blocked by F-02 |

## Open Roadmap Questions

(None — PRD has no open questions, and the interview surfaced no cross-cutting unknowns. Per-slice unknowns live in S-02, S-03.)

## Parked

- **FR-008 (AI-generated insight)** — Why parked: PRD marks it "nice-to-have"; main_goal=speed + top_blocker=time force strict must-have path. AI insight can come post-MVP.
- **NFR "responsive on mobile browsers"** — Why parked: not parked entirely, but not an explicit slice. S-01/S-02 will use Django templates + basic CSS; mobile responsiveness is implicit in the ≤3 taps guardrail. No dedicated "mobile polish" slice.
- **Complex charts / analytics** — Why parked: PRD §Non-Goals "No complex charts". Dashboard shows one number (daily limit), one status (on-track yes/no). Post-MVP can add spending history or trends.
- **Observability foundation (logging, error tracking)** — Why parked: main_goal=speed defers non-blocking infrastructure. Django's default logging + Railway logs are sufficient for MVP. Sentry/metrics can come post-launch.
- **Bank integrations** — Why parked: PRD §Non-Goals "No bank integrations — manual entry only".
- **Receipt scanning (OCR)** — Why parked: PRD §Non-Goals "No receipt scanning".
- **OAuth (Google/Facebook login)** — Why parked: PRD FR-001 Socrates note: "Email/password is simpler for MVP. OAuth can be added post-MVP."

## Done

(Empty on first generation. `/10x-archive` appends an entry here — and flips that item's `Status` to `done` — when a change whose `Change ID` matches the item is archived.)
