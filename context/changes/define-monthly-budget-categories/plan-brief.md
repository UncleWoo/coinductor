# Define Monthly Budget Categories — Plan Brief

> Full plan: `context/changes/define-monthly-budget-categories/plan.md`

## What & Why

S-03 adds the missing user-facing flow to define monthly category budgets, which is required for Coinductor’s core daily-limit loop. Without this, users stay in a no-budget placeholder state and cannot get meaningful budget guidance.

## Starting Point

The data model is already ready: categories exist per user, default categories are seeded automatically, and `Budget` has per-user-per-category-per-month uniqueness. What’s missing is dashboard-side form handling and UI to create/edit current-month budget values.

## Desired End State

From the dashboard, users can set and edit current-month category budgets in one flow, optionally add a custom category, and immediately see dashboard move out of no-budget state. Saved data uses idempotent upsert semantics and preserves existing S-01 metrics behavior.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) |
| --- | --- | --- |
| Scope | Current-month setup only | Delivers MVP value quickly without multi-month complexity. |
| Category strategy | Predefined + custom category creation in setup | Keeps defaults while allowing user flexibility you requested. |
| Save semantics | Upsert by user/category/month | Supports repeat edits without duplicate-row failures. |
| Entry point | Inline dashboard flow on `home` | Shortest path from no-budget warning to completion. |
| Validation | Amounts `>= 0` and at least one `> 0` | Prevents unusable all-zero setup while keeping partial zero budgets possible. |
| Multi-form handling | Action-dispatched POST on `home` | Avoids collisions with planned S-02 quick-add flow. |
| Testing depth | Unit/form + integration + template assertions | Balances confidence and delivery speed. |
| Done criteria | Save/edit budgets and instantly reflect dashboard state | Verifies the real user feedback loop, not just DB writes. |

## Scope

**In scope:** dashboard budget setup UI, current-month upsert persistence, custom category creation in setup, validation and tests.

**Out of scope:** multi-month management, category deletion lifecycle, historical budget analytics, S-01 formula changes.

## Architecture / Approach

Keep the existing FBV architecture by extending `home` with action-routed POST handling. Use dedicated form logic in `budget/forms.py` for validation and category handling, persist budgets with create-or-update keyed by `(user, category, current_month)`, then rely on current dashboard service recomputation after PRG redirect.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Budget Setup Form Layer | Validation-safe forms for budgets and custom category input | Validation gaps causing inconsistent setup behavior |
| 2. Dashboard POST Orchestration and Upsert | Reliable action-dispatched submit + idempotent save flow | Route complexity with multiple dashboard actions |
| 3. Dashboard Budget Setup UI Integration | Working no-budget and edit UX in `home.html` | Template regressions in existing dashboard states |
| 4. S-03 Final Verification and Stability | Consolidated test/manual acceptance pass | Hidden edge cases around updates and constraints |

**Prerequisites:** F-02 data model is present; S-01 dashboard is active.
**Estimated effort:** ~2-3 sessions across 4 phases.

## Open Risks & Assumptions

- Custom category creation may increase validation and UX complexity versus strict predefined-only mode.
- Dashboard POST branching must stay explicit to avoid S-02 integration drift.
- All-zero submissions are intentionally invalid and need clear user messaging.

## Success Criteria (Summary)

- User can define and edit current-month category budgets from dashboard.
- Dashboard leaves no-budget state and shows updated metrics immediately after valid save.
- Validation and integration tests cover setup success/error paths and prevent regressions.
