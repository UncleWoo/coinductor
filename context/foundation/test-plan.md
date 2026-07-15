# Test Plan

> Phased test rollout for this project. Strategy is frozen at the top
> (§1–§5); cookbook patterns at the bottom (§6) fill in as phases ship.
> Read before writing any new test.
>
> Refresh: re-run `/10x-test-plan --refresh` when stale (see §8).
>
> Last updated: 2026-07-09

## 1. Strategy

Tests follow three non-negotiable principles for this project:

1. **Cost × signal.** The cheapest test that gives a real signal for the risk wins. Do not promote to e2e because e2e "feels safer." Do not put an AI-native visual layer on top of deterministic checks when deterministic checks already catch the regression.
2. **User concerns are first-class evidence.** Risks anchored in interview concerns (especially around user experience and dashboard/UI confidence) carry the same weight as PRD or roadmap statements.
3. **Risks are scenarios, not code locations.** This plan documents *what could fail* and *why we believe it is likely* from PRD, roadmap, interview, and churn signal. It does **not** claim to know which line owns the failure. That grounding is produced by `/10x-research` during each rollout phase. If this plan and research disagree on failure location, research is the ground truth.

This project is a Django budget app whose core promise is behavioral guidance, not bookkeeping alone: users should trust the on-track status and dynamic daily limit after every budget or expense change. The highest-risk outcomes are therefore wrong spend guidance and degraded entry flow usability (`≤3 taps/clicks`) rather than low-level framework mechanics. Existing tests are minimal (test-base profile `none`), so rollout starts by establishing integration-level protection on critical user paths before adding broader coverage. Because the user explicitly excluded infra/config spend in the interview, rollout focuses test budget on product behavior, authorization boundaries, and input/duplication failure modes, while keeping infra-heavy validation out of scope unless future risk evidence changes.

Hot-spot scope used for likelihood weighting: `budget/`, `coinductor/`, `static/css/`.

## 2. Risk Map

The top failure scenarios this project must protect against, ordered by risk = impact × likelihood. Risks are user/business failures, not test names. The Source column cites evidence that surfaced the risk (not code anchors).

| # | Risk (failure scenario) | Impact | Likelihood | Source (evidence — not anchor) |
|---|---|---|---|---|
| 1 | Daily limit or on-track status is wrong after budget/expense changes, so the user gets misleading spend guidance. | High | High | PRD FR-006/FR-007; roadmap S-01; interview Q3; hot-spot dir `coinductor/` (35 changes/30d) |
| 2 | Expense entry no longer meets the ≤3 taps/clicks guardrail, reducing ongoing usage. | High | High | PRD success guardrail; roadmap S-02; interview Q1/Q3 |
| 3 | Authenticated user can read or mutate another user’s budget/expense data (authorization/ownership failure). | High | Medium | PRD Access Control + single-user ownership model; tech-stack auth baseline; abuse lens |
| 4 | Duplicate submit/retry records extra expenses and distorts remaining budget/velocity. | Medium | Medium | PRD expense tracking + dashboard state requirements; roadmap S-02; interview Q1 |
| 5 | Dashboard state rendering regresses (no-budget/no-expense/metrics states), so users cannot reliably interpret status. | High | Medium | PRD US-01 acceptance criteria; roadmap S-01/S-04; interview Q3; hot-spot dir `coinductor/templates/` (25 changes/30d) |
| 6 | Server-side validation diverges from UI expectations (invalid data accepted or valid data rejected inconsistently). | Medium | Medium | PRD manual-entry constraints; roadmap S-02; abuse lens (untrusted input) |

### Risk Response Guidance

| Risk | What would prove protection | Must challenge | Context `/10x-research` must ground | Likely cheapest layer | Anti-pattern to avoid |
|------|-----------------------------|----------------|--------------------------------------|-----------------------|-----------------------|
| #1 | Recomputed outputs remain behaviorally correct after budget/expense changes and date progression. | “Formula is simple so it cannot fail.” | Source-of-truth for totals, month boundaries, and recalculation triggers. | Integration | Copying expected values from production calculation logic. |
| #2 | Add-expense flow remains usable within guardrail and shows updated state immediately after submit. | “Page renders means flow is still usable.” | Submit/redirect/render cycle and state update signal shape. | Integration + focused smoke | Snapshot/class-only assertions. |
| #3 | Cross-user access attempts fail for both read and write paths. | “Authenticated means authorized.” | Ownership checks at request boundary and persisted object filters. | Integration | Single-user happy-path-only tests. |
| #4 | Repeated action does not duplicate accounting side effects. | “One POST in a test represents real usage.” | Duplicate handling and persistence-side behavior under repeats. | Integration | Over-mocking persistence/external boundaries. |
| #5 | Each dashboard state presents correct user-facing signals under the right preconditions. | “One state passing implies all states are safe.” | State-branching preconditions and fallback display rules. | Integration/template | Only testing the default happy dashboard state. |
| #6 | Invalid input is rejected server-side with stable error behavior; valid input passes. | “Client-side validation is enough.” | Server form validation and error-path behavior contract. | Integration/form | Testing only browser/client constraints. |

## 3. Phased Rollout

Each row is a rollout phase with its own change folder. Status values are parser literals and must stay unchanged.

| # | Phase name | Goal (one line) | Risks covered | Test types | Status | Change folder |
|---|---|---|---|---|---|---|
| 1 | Critical-path baseline | Bootstrap the test baseline and protect dashboard + expense entry behavior first. | #1, #2, #5 | integration-first (+ minimal unit where cheap) | change opened | context/changes/testing-critical-path-baseline/ |
| 2 | Abuse + validation boundaries | Lock ownership and untrusted-input protections at request boundaries. | #3, #6 | integration / contract-style request tests | not started | — |
| 3 | Duplicate-action resilience | Prevent accounting drift from repeated submit/retry behavior. | #4 (and #1 overlap) | integration | not started | — |
| 4 | Quality-gates + cookbook hardening | Wire required gates and codify repeatable add-test patterns. | cross-cutting | gates + cookbook updates | not started | — |

## 4. Stack

| Layer | Tool | Version | Notes |
|---|---|---|---|
| unit + integration | Django test runner (`manage.py test`) | Django 6.0.6 | Present but sparse suite; Phase 1 establishes baseline conventions. |
| API mocking | none yet | n/a | Add only if needed to reduce external-boundary flakiness. |
| e2e | none yet — see §3 Phase 1 | n/a | Start with integration unless a full-browser signal is required. |
| accessibility | none yet — see §3 Phase 4 | n/a | Introduce only if tied to explicit risk/gate signal. |
| (optional) AI-native | none yet | n/a | Add only when deterministic layers cannot cheaply catch a risk. |

**Stack grounding tools (current session):**
- Docs: none — no Context7/framework docs MCP exposed; checked: 2026-07-09
- Search: `web_fetch` available — not needed in Phase 1 because local PRD/roadmap/stack docs were sufficient; checked: 2026-07-09
- Runtime/browser: none — no Playwright/browser MCP exposed; checked: 2026-07-09
- Provider/platform: GitHub (`gh`, GitHub MCP) available — relevant for future quality-gate and workflow verification; checked: 2026-07-09

## 5. Quality Gates

| Gate | Where | Required? | Catches |
|---|---|---|---|
| lint + typecheck | local + CI | required after §3 Phase 4 | static drift and type-level regressions |
| unit + integration | local + CI | required after §3 Phase 1 | behavior and business-logic regressions |
| e2e on critical flows | CI on PR | planned (evaluate in §3 Phase 1) | cross-layer UX failures not caught cheaper |
| post-edit hook | local (agent loop) | recommended after §3 Phase 4 | immediate regression detection while editing |
| visual diff (deterministic) | CI on PR | optional after §3 Phase 4 | layout/regression drift in key screens |
| multimodal visual review | selective CI/manual | optional | visual issues deterministic checks miss |
| pre-prod smoke | between merge + prod | optional | environment-specific breakage |

## 6. Cookbook Patterns

How to add new tests in this project. Placeholders are filled as rollout phases complete.

### 6.1 Adding a unit test

TBD — see §3 Phase 1 for core daily-limit behavior pattern.

### 6.2 Adding an integration test

TBD — see §3 Phase 1 for dashboard-state and expense-entry protection pattern.

### 6.3 Adding an abuse/authorization test

TBD — see §3 Phase 2 for ownership-boundary denial/regression pattern.

### 6.4 Adding a duplicate-action resilience test

TBD — see §3 Phase 3 for repeated-submit accounting protection pattern.

### 6.5 Wiring or extending quality gates

TBD — see §3 Phase 4 for durable local/CI gate pattern.

### 6.6 Per-rollout-phase notes

TBD — append brief lessons after each phase lands.

## 7. What We Deliberately Don't Test

- **Infra/configuration-heavy behavior** — explicitly excluded by interview Q5 (`infra, configuration`) to keep budget on product-risk signal. Re-evaluate if deployment/runtime incidents become top-3 risks.
- **Generated/build output verification as primary risk gate** — build artifacts (for example minified CSS output) are not first-order product-risk tests; treat them as supporting checks only.

## 8. Freshness Ledger

- Strategy (§1–§5) last reviewed: 2026-07-09
- Stack versions last verified: 2026-07-09
- AI-native tool references last verified: 2026-07-09

Refresh (`/10x-test-plan --refresh`) when:

- a new top-3 risk surfaces from roadmap/archive activity,
- a recommended tool `checked:` date is older than three months,
- the project stack or test runner strategy changes,
- §7 negative-space no longer matches current team belief.
