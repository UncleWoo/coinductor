# Add Expense in Three Taps — Plan Brief

> Full plan: `context/changes/add-expense-three-taps/plan.md`
> Research: `context/changes/add-expense-three-taps/research.md`

## What & Why

This plan implements S-02: users add an expense directly from dashboard in ≤3 taps/clicks and immediately see recalculated budget feedback. It turns the existing read-only S-01 dashboard into an action loop, which is required for daily habit formation and product retention. Without fast entry plus instant feedback, the core rebalancing value weakens.

## Starting Point

Dashboard already exists (`home` + `get_dashboard_metrics`) with status/limit cards, but it has no expense-entry form or POST handling. Data model supports expenses and ownership validation, and tests already cover dashboard rendering/service math.

## Desired End State

Authenticated users can submit amount/category/date from an inline quick-add card near dashboard metrics. Successful submit redirects back to dashboard with updated values and clear feedback; invalid submit keeps values and shows inline errors. Entry remains available in no-budget state with warning visible.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
| --- | --- | --- | --- |
| Entry in no-budget state | Allowed with warning | Avoids blocking user action before S-03 and keeps onboarding momentum | Plan |
| Category selection | All user-owned active categories | Matches ownership model and avoids hidden exclusions | Plan |
| Date behavior | Prefilled to today, editable inline | Preserves speed while allowing correction/backdating | Plan |
| Submission flow | POST-Redirect-GET on `home` | Fits current server-rendered FBV architecture and ensures clean instant recalc | Research + Plan |
| Error UX | Inline field errors with value retention | Fast correction loop and consistent with current form patterns | Plan |
| Scope cutoff | Prioritize quick-add + recalc core over UI polish extras | Protects must-have behavior under time pressure | Plan |

## Scope

**In scope:**
- Quick-add expense form (`amount`, `category`, `date`) on dashboard.
- Home POST handling for create + instant metric recalculation.
- Inline validation errors and success feedback.
- Form, integration, and metric-update test coverage.

**Out of scope:**
- API/HTMX/SPA submission architecture.
- Advanced recurring expenses and automation.
- Major dashboard redesign beyond quick-add card.
- Additional analytics/charting.

## Architecture / Approach

Use existing `home` FBV as the single dashboard interaction endpoint: GET renders metrics + quick-add; POST validates and saves expense via user-scoped form, then redirects to `home` where `get_dashboard_metrics` recalculates the cards. This keeps architecture consistent and minimizes moving parts.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Expense Form and Validation Layer | User-scoped expense form + validation tests | Ownership/validation gaps may leak incorrect categories |
| 2. Dashboard POST Flow Wiring | Reliable PRG create flow with metric refresh | Incorrect POST error path may lose form state |
| 3. Inline Quick-Add Dashboard UX | ≤3-tap quick-add card with feedback and state handling | UI density could reduce clarity on small screens |
| 4. End-to-End Verification and Stability Pass | Final regression-safe S-02 validation | Hidden UX regressions if manual checks are shallow |

**Prerequisites:** F-01, F-02, S-01 already implemented and stable.
**Estimated effort:** ~2-3 sessions across 4 phases.

## Open Risks & Assumptions

- Assumes users can add expenses before monthly budget setup without confusion.
- Assumes current dashboard layout can absorb quick-add card without hurting scannability.
- Assumes current aggregate recalculation remains performant after frequent submits.

## Success Criteria (Summary)

- User can add expense from dashboard in ≤3 interactions on common path.
- Dashboard metrics/status visibly update right after successful submit.
- Invalid input is recoverable inline without data loss or navigation breakage.
