---
date: 2026-06-30T00:14:42+02:00
researcher: Copilot
git_commit: a2e922e854c8efa8559620b20d6bda2c3158470e
branch: main
repository: UncleWoo/coinductor
topic: "Planning analysis for add-expense-three-taps (S-02)"
tags: [research, codebase, dashboard, expenses, s-02]
status: complete
last_updated: 2026-06-30
last_updated_by: Copilot
---

# Research: Planning analysis for add-expense-three-taps (S-02)

**Date**: 2026-06-30T00:14:42+02:00
**Researcher**: Copilot
**Git Commit**: a2e922e854c8efa8559620b20d6bda2c3158470e
**Branch**: main
**Repository**: UncleWoo/coinductor

## Research Question

Determine best-fit architecture for adding expense from dashboard (<=3 taps), preserving existing Django patterns and testing strategy.

## Summary

Best fit is **POST-on-home function-based view (FBV)** with a lightweight Django `ModelForm` bound in the dashboard template. This matches existing routing/view conventions, preserves server-rendered UX, and enables instant recalculation by redirecting back to `home` where metrics are already recomputed.

## Detailed Findings

### Dashboard architecture and flow

- Home route is already the dashboard entrypoint: `path('', app_views.home, name='home')` ([coinductor/urls.py:23](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/urls.py#L23)).
- Home is an authenticated FBV that renders dashboard context from a service ([coinductor/views.py:39-52](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/views.py#L39-L52)).
- Dashboard metrics (remaining budget, daily limit, on-track, velocity) are centralized in `get_dashboard_metrics` ([budget/services.py:47-108](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/budget/services.py#L47-L108)).
- `home.html` already contains the target visual context where immediate feedback is displayed ([coinductor/templates/home.html:44-86](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/templates/home.html#L44-L86)).

### Validation and error handling patterns

- Domain ownership validation is model-level via `clean()` + `ValidationError` on `Budget` and `Expense` ([budget/models.py:68-73](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/budget/models.py#L68-L73), [budget/models.py:92-97](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/budget/models.py#L92-L97)).
- Existing view-level pattern handles validation errors by attaching field errors and re-rendering template (`form.add_error`) ([coinductor/views.py:11-28](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/views.py#L11-L28)).
- Templates render first field error + non-field error blocks ([coinductor/templates/registration/signup.html:20-22](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/templates/registration/signup.html#L20-L22), [coinductor/templates/registration/signup.html:53-57](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/templates/registration/signup.html#L53-L57)).
- Tests validate model invariants via `full_clean()` and `assertRaises(ValidationError)` ([budget/tests.py:24-45](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/budget/tests.py#L24-L45)).

### Testing baseline

- Integration tests already assert home auth behavior and dashboard rendering states ([coinductor/tests.py:13-105](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/coinductor/tests.py#L13-L105)).
- Service tests already cover recalculation math, month scoping, and edge states for dashboard values ([budget/tests.py:70-267](https://github.com/UncleWoo/coinductor/blob/a2e922e854c8efa8559620b20d6bda2c3158470e/budget/tests.py#L70-L267)).

## Code References

- `coinductor/urls.py:23-27` - Route topology and home naming convention.
- `coinductor/views.py:39-52` - Current dashboard FBV.
- `coinductor/views.py:11-28` - Existing POST + validation handling style.
- `coinductor/templates/home.html:44-86` - Dashboard metric/velocity section suitable for inline quick-add form.
- `budget/services.py:47-108` - Recalculation source of truth.
- `budget/models.py:79-97` - Expense schema and ownership validation.
- `budget/tests.py:24-45` - Validation test style.
- `coinductor/tests.py:26-100` - Home integration test style.

## Architecture Insights

- The repo favors **server-rendered Django FBV + template composition** over API-first interactions.
- There is no current DRF/HTMX/front-end state layer; introducing API endpoints would add a second architecture style without existing supporting patterns.
- The fastest “instant recalculation” path is PRG: POST expense -> redirect `home` -> `get_dashboard_metrics` recomputes.

## Historical Context (from prior changes)

- S-01 plan explicitly chose keeping the dashboard on the existing home FBV and centralizing calculations in `budget/services.py` (`context/changes/dashboard-on-track-daily-limit/plan.md:5-6`, `41-44`).
- S-01 implementation/testing established `home` as the canonical budget-feedback surface (`context/changes/dashboard-on-track-daily-limit/plan.md:110-141`, progress section).

## Related Research

- `context/changes/dashboard-on-track-daily-limit/research.md`
- `context/changes/dashboard-on-track-daily-limit/plan.md`

## Open Questions

1. In S-02, should expense entry be allowed when `empty_state == "no_budget"`, or blocked until S-03 budget setup?
2. Should quick-add category choices include all user categories or only categories with current-month budgets?
3. Should default date be “today” and remain editable inline, or prefilled hidden for minimum taps?
4. Should success feedback use Django messages banner (`base.html:25-33`) or silent refresh with updated cards only?
