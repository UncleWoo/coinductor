---
project: "Coinductor"
context_type: greenfield
created: 2026-06-05
updated: 2026-06-05
checkpoint:
  current_phase: 8
  phases_completed: [1, 2, 3, 4, 5, 6, 7]
  gray_areas_resolved:
    - topic: "pain category"
      decision: "workflow friction — no daily feedback loop"
    - topic: "competitive insight"
      decision: "existing apps lack the 'X zł per day' mental model"
    - topic: "primary persona scope"
      decision: "an individual managing their own budget (self-use case)"
    - topic: "auth strategy"
      decision: "email + password login, data syncs across devices"
    - topic: "user model"
      decision: "flat — one account = one budget, no sharing"
    - topic: "mvp timeline"
      decision: "~3 weeks after-hours; scoped to core rebalancing"
  frs_drafted: 8
  quality_check_status: accepted
---

# Shape Notes — Coinductor

## Vision & Problem Statement

Users don't stick to their budgets because they lack daily feedback. They discover overspend at month-end when it's too late to adjust. The cost today is broken budgets and reactive panic.

The insight: existing budget apps show static monthly numbers. The "X zł per day" mental model creates a daily feedback loop that changes behavior — users know exactly how much they can spend today, recalculated after every expense.

## User & Persona

**Primary persona:** An individual managing their own personal budget — including the developer themselves. They have recurring income, regular expenses, and want to stay on track without spreadsheet complexity. They feel the pain when they check finances at month-end and realize they've overspent with no time to correct.

They don't need bank integrations, shared budgets, or complex analytics — they need a daily spending limit that updates in real time.

## Access Control

**Auth model:** Login with email + password. Data syncs across devices via server.

**User model:** Flat — each user account owns exactly one budget. No roles, no sharing, no household/team features. One account = one budget = one user's view.

## Success Criteria

### Primary
- User can answer "am I on track with my budget?" and get a clear yes/no answer

### Secondary
- User opens the app at least once daily

### Guardrails
- Data entry (adding an expense) completes in ≤ 3 taps/clicks from the main screen

## User Stories

### US-01: User checks if they're on track

- **Given** a user with a defined monthly budget and some logged expenses
- **When** they open the dashboard
- **Then** they see a clear yes/no answer whether they're on track, along with remaining budget, days left, and daily spending limit (e.g., "You can spend 67 zł/day")

#### Acceptance Criteria
- Dashboard shows on-track status prominently (yes/no or green/red)
- Daily limit recalculates correctly after each new expense
- Empty state (no expenses yet) shows helpful guidance

## Functional Requirements

### Authentication
- FR-001: User can sign up with email and password. Priority: must-have
  > Socrates: Counter-argument: "Email/password is friction — users expect OAuth in 2026." Resolution: kept; email/password is simpler for MVP. OAuth can be added post-MVP.

- FR-002: User can log in to access their budget data. Priority: must-have

### Budget Setup
- FR-003: User can define monthly budget categories (e.g., food: 2000, transport: 500). Priority: must-have
  > Socrates: Counter-argument: "Fixed categories might not match how users think about spending." Resolution: kept; predefined categories are simpler. Custom categories can come later.

### Expense Tracking
- FR-004: User can add an expense (amount, category, date). Priority: must-have
  > Socrates: Counter-argument: "Manual entry is why users abandon budget apps — they forget or it's tedious." Resolution: kept; manual entry is core. Speed guardrail (≤ 3 taps) mitigates friction.

### Budget State
- FR-005: User can view current budget state (spent, remaining, days left). Priority: must-have

### Auto-Rebalancing (Core)
- FR-006: User can see dynamic daily limit (remaining_money / remaining_days). Priority: must-have
  > Socrates: Counter-argument: "A simple division ignores spending patterns — weekends cost more than weekdays." Resolution: kept; the formula is simple and transparent. Pattern-aware limits can come later.

### Dashboard
- FR-007: User can view dashboard showing: on-track status, remaining budget, spending velocity, daily limit. Priority: must-have

### AI Insight
- FR-008: User can see one AI-generated insight per day (prediction, cause, recommendation). Priority: nice-to-have
  > Socrates: Counter-argument: "AI insights are often generic and unhelpful." Resolution: kept as nice-to-have; AI adds value but isn't core. Core is rebalancing.

## Non-Functional Requirements

- Expense entry completes in ≤ 3 taps/clicks from the main screen — speed is critical to prevent abandonment
- Web app is responsive and usable on mobile browsers

## Business Logic

**One-sentence rule:** The app calculates remaining budget divided by remaining days to show a dynamic daily spending limit.

This distinguishes the app from a generic expense tracker — it doesn't just record spending, it tells you how much you can spend today.

**Inputs:** Monthly budget (per category), logged expenses (amount, category, date), current date.

**Output:** Daily limit ("You can spend X zł/day"), on-track status (yes/no — are you above or below the sustainable daily spend rate?).

**User encounter:** On dashboard open, user immediately sees their daily limit prominently displayed alongside on-track status. After adding an expense, the limit recalculates instantly.

## Non-Goals

- **No mobile app** — web only for MVP. Responsive web serves mobile users initially.
- **No multiple users / shared budgets** — single user per account only. No inviting partners, no role-based access.
- **No bank integrations** — manual entry only. Bank APIs vary by region and add significant complexity.
- **No receipt scanning (OCR)** — manual entry is the core flow.
- **No complex charts** — keep the dashboard simple. One insight, one limit, one status.
- **No ML-trained predictions** — simple formula (remaining/days) only. ML can come post-MVP.
- **No advanced settings / customization** — sensible defaults only.

## Product Framing (PRD Frontmatter)

- **product_type:** web-app
- **target_scale:** { users: medium, qps: low, data_volume: small }
- **timeline_budget:** { mvp_weeks: 3, hard_deadline: null, after_hours_only: true }
