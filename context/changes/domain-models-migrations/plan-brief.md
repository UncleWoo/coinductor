# Domain Models & Migrations — Plan Brief

> Full plan: `context/changes/domain-models-migrations/plan.md`

## What & Why

Define the core data models (Category, Budget, Expense) that power Coinductor's daily limit calculation. Users lack daily budget feedback — they overspend and only discover it at month-end. These models enable the "X zł per day" mental model: `remaining_money / remaining_days`, recalculated after every expense.

## Starting Point

- No custom models exist — only Django built-in apps
- Auth is complete (email/password signup/login via F-01)
- Database: SQLite (dev), PostgreSQL (prod)
- Project is monolithic — no separate Django apps yet

## Desired End State

A `budget` Django app with three models: Category, Budget, Expense. New users get default categories seeded on signup. All models have soft-delete support (`is_deleted` flag) and are registered in Django admin. Schema is ready for S-01 (dashboard), S-02 (expense entry), S-03 (budget setup).

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
|----------|--------|------------------|--------|
| Category handling | Separate `Category` model | Flexibility for user-defined categories later | Plan |
| Initial categories | Seed defaults on signup | Fast onboarding, no empty state | Plan |
| Budget scope | Per category per month | Matches PRD exactly ("monthly budget per category") | Plan |
| Expense linking | Links to Category only | Simple; daily limit aggregates across all categories | Plan |
| Deletion behavior | Soft delete (`is_deleted`) | Preserves historical data for calculations | Plan |
| Project structure | New `budget` Django app | Standard convention, clean separation | Plan |

## Scope

**In scope:**
- Category, Budget, Expense models with User FK
- Soft-delete support (`is_deleted` flag)
- Timestamps (`created_at`, `updated_at`)
- Django migrations
- Admin registration
- Default category seeding on signup

**Out of scope:**
- Views, URLs, templates (S-01/S-02/S-03)
- Daily limit calculation logic (S-01)
- API endpoints
- Custom category creation UI
- Budget copying between months

## Architecture / Approach

```
User (django.contrib.auth)
  └── Category (name, is_deleted, timestamps)
        ├── Budget (category FK, month, amount)
        └── Expense (category FK, amount, date, description)
```

New `budget/` Django app with models.py, admin.py, signals.py. Signal hooks into User post_save to seed default categories. All models use soft-delete pattern.

## Phases at a Glance

| Phase | What it delivers | Key risk |
|-------|-----------------|----------|
| 1. Create budget app & models | App scaffolded, models defined | None — straightforward Django |
| 2. Migrations & admin | Schema applied, admin visible | Migration conflicts if run on existing prod data |
| 3. Seed default categories | New users get 7 categories on signup | Signal must fire only on creation, not updates |
| 4. Final verification | End-to-end confirmation | None — verification only |

**Prerequisites:** F-01 (auth) must be complete — user signup flow must exist for seeding to hook into.  
**Estimated effort:** ~1-2 sessions (single phase stream)

## Open Risks & Assumptions

- Assumes no users in production yet (or existing users won't get default categories without data migration)
- Budget unique constraint (user, category, month) may need adjustment if users want multiple budget entries per category/month

## Success Criteria (Summary)

- New user signup → 7 default categories auto-created
- Can create Budget and Expense entries via admin
- Soft-delete works (record persists with `is_deleted=True`)
- `makemigrations --check` shows no pending migrations
