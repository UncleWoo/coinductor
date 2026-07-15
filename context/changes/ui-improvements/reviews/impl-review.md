<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: UI improvements from S-04 roadmap slice

- **Plan**: context/changes/ui-improvements/plan.md
- **Scope**: Phase 1, 2, 3, 4 of 4
- **Date**: 2026-07-09
- **Verdict**: REJECTED
- **Findings**: 1 critical, 3 warnings, 2 observations

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| Plan Adherence | WARNING |
| Scope Discipline | PASS |
| Safety & Quality | FAIL |
| Architecture | PASS |
| Pattern Consistency | WARNING |
| Success Criteria | FAIL |

## Findings

### F1 — Test password placeholders cause 8 test failures

- **Severity**: ❌ CRITICAL
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Safety & Quality
- **Location**: coinductor/tests.py (multiple lines: 15, 44, 58, 73, etc.)
- **Detail**: Multiple test methods contain `******` placeholder values for passwords. These masked values cause test failures. Test suite shows 8 failures: 2 KeyError exceptions for missing `velocity_status` context keys, and 6 assertion failures related to budget setup and custom category logic that expect redirects or specific status codes.
- **Fix**: Replace all `******` password placeholders with actual test password values (e.g., `"testpass123"`) or use `self.password` variable consistently throughout tests.
  - Strength: Fixes the immediate test failures; standard Django test pattern.
  - Tradeoff: Minor — search-and-replace across test file.
  - Confidence: HIGH — passwords were redacted during implementation; restoring them unblocks tests.
  - Blind spot: None significant.
- **Decision**: FIXED

### F2 — Broken ui_card.html partial using non-standard pattern

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Plan Adherence + Pattern Consistency
- **Location**: coinductor/templates/partials/ui_card.html
- **Detail**: Plan specified "reusable card partial that accepts block content." Implementation uses `{{ content|default:"" }}` variable instead of Django's standard `{% block %}` pattern. This partial cannot wrap template blocks elegantly and appears unused in the codebase. The pattern agent notes this doesn't match how `expense_form.html` partial works (self-contained section). The drift agent flagged this as implementation pattern drift.
- **Fix A ⭐ Recommended**: Remove the partial and use `class="ui-card"` directly in templates
  - Strength: Simplifies codebase; `.ui-card` CSS class can be applied directly without indirection. Templates already use this pattern successfully in home.html and auth screens.
  - Tradeoff: Loses the partial abstraction, but it wasn't being used correctly anyway.
  - Confidence: HIGH — grepping the codebase shows no includes of this partial with a `content` parameter.
  - Blind spot: None significant.
- **Fix B**: Restructure partial to use Django block pattern
  - Strength: Preserves the "reusable wrapper" concept from the plan.
  - Tradeoff: More complex — requires base template + extends pattern. Adds complexity for minimal benefit when a CSS class works.
  - Confidence: MEDIUM — would work but adds architectural overhead for simple styling.
  - Blind spot: Whether any future work planned to depend on this partial pattern.
- **Decision**: FIXED (via Fix A)

### F3 — Unplanned expense_form.html partial

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Scope Discipline
- **Location**: coinductor/templates/partials/expense_form.html (NEW)
- **Detail**: New partial extraction not mentioned in any phase's "Changes Required" section. The drift agent notes this follows Phase 2's DRY pattern (reducing template duplication) and is used twice in home.html with different contextual help text. Functionally beneficial but technically scope creep.
- **Fix**: Document in the plan as a Phase 2 addendum under "Changes Required"
  - Strength: Updates source of truth; aligns with Phase 2's "reduce template duplication" goal. The partial follows proper Django patterns (complete, self-contained, accepts context variables).
  - Tradeoff: Plan becomes slightly retroactive.
  - Confidence: HIGH — extraction is consistent with Phase 2's stated goals and improves maintainability.
  - Blind spot: None significant.
- **Decision**: FIXED

### F4 — Missing context key safeguards in templates

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Safety & Quality (Reliability)
- **Location**: coinductor/templates/home.html (multiple locations)
- **Detail**: Template context keys like `dashboard.remaining_budget`, `dashboard.daily_limit`, `dashboard.velocity_status` are accessed without null/existence checks. If the view fails to provide these keys, template will error. Current test failures show `KeyError: 'velocity_status'` in 2 tests, indicating the view doesn't always provide expected context.
- **Fix**: Add defensive checks in templates using `{% if dashboard %}...{% endif %}` or ensure view always provides complete context
  - Strength: Prevents template errors when view contract isn't fulfilled; defensive programming.
  - Tradeoff: Adds verbosity to templates; alternative is fixing view to guarantee context.
  - Confidence: HIGH — test failures prove this is a real issue, not theoretical.
  - Blind spot: Root cause may be in the view logic, not templates — fixing templates may mask view bugs.
- **Decision**: FIXED

### F5 — Missing user confirmation for category deletion

- **Severity**: 💡 OBSERVATION
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Safety & Quality (Data Safety)
- **Location**: coinductor/templates/home.html (category delete forms)
- **Detail**: Category deletion via POST with hidden form fields. No JavaScript confirmation prompt before deletion. Functionally safe (requires POST, CSRF protected) but UX could be improved.
- **Fix**: Add onclick confirmation: `onclick="return confirm('Remove this category?');"` to delete buttons
  - Strength: Prevents accidental deletions; standard UX pattern.
  - Tradeoff: Minimal — one attribute per delete button.
  - Confidence: HIGH — standard pattern for destructive actions.
  - Blind spot: None significant.
- **Decision**: FIXED

### F6 — Test assertions shifted but view context incomplete

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Success Criteria
- **Location**: coinductor/tests.py + coinductor/views.py (implied)
- **Detail**: Phase 4 successfully migrated tests from brittle class checks to semantic context assertions (e.g., `response.context["velocity_status"]`). However, 2 tests now fail with `KeyError: 'velocity_status'` because the view doesn't provide this context key in all states. Plan specified "no template context key regressions" as automated criterion 3.2, but the implementation introduced new key assumptions without updating view logic.
- **Fix A ⭐ Recommended**: Update view to always provide `velocity_status` context (even if None or a default value)
  - Strength: Fulfills view-template contract; tests pass; aligns with Phase 4's semantic assertion goal.
  - Tradeoff: Requires view code changes (not in plan scope, but necessary for tests to pass).
  - Confidence: HIGH — view must match what tests expect, or tests are meaningless.
  - Blind spot: Whether other context keys have similar gaps.
- **Fix B**: Revert test assertions to check rendered text instead of context keys
  - Strength: Tests pass without view changes; stays within template-only scope.
  - Tradeoff: Abandons Phase 4's "prefer semantic assertions" goal; returns to brittle text checks.
  - Confidence: MEDIUM — solves test failures but undermines the phase's stated improvement.
  - Blind spot: None significant.
- **Decision**: FIXED (via Fix A - same fix as F4)
