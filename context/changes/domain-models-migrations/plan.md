# Domain Models & Migrations Implementation Plan

## Overview

Define the core data models for Coinductor's budget tracking: Category, Budget, and Expense. These models form the foundation for the daily limit calculation (`remaining_money / remaining_days`) and unlock S-01 (dashboard), S-02 (expense entry), and S-03 (budget setup).

## Current State Analysis

- **No custom models exist** — project uses only Django built-in apps
- **Auth is complete** — users sign up with email (stored as username), using Django's default User model
- **Database:** SQLite3 (dev), PostgreSQL (prod via DATABASE_URL)
- **Project structure:** Monolithic `coinductor/` folder — no separate Django apps yet

### Key Discoveries:

- `coinductor/settings.py:58-65` — INSTALLED_APPS contains only Django built-ins
- `coinductor/views.py:8-25` — Signup view creates User but no post-signup hooks exist yet
- `db.sqlite3` exists (131KB) with Django auth migrations applied

## Desired End State

After this plan completes:

1. A `budget` Django app exists with three models: `Category`, `Budget`, `Expense`
2. All models are owned by a User (ForeignKey) with soft-delete support (`is_deleted` flag)
3. Migrations are applied; database schema is ready for S-01/S-02/S-03
4. Default categories (Food, Transport, Entertainment, etc.) are auto-seeded on user signup
5. All models are registered in Django admin for debugging/data inspection

**Verification:** 
- `python manage.py makemigrations --dry-run` shows no pending migrations
- Django admin shows Category, Budget, Expense models
- Creating a new user via signup auto-creates default categories

## What We're NOT Doing

- No views, URLs, or templates — those come in S-01/S-02/S-03
- No business logic for daily limit calculation — that's S-01
- No API endpoints — data layer only
- No custom category creation UI — seeding covers MVP
- No budget copying between months — manual setup for now

## Implementation Approach

Create a new Django app `budget` following standard conventions. Define three models with clear ownership (User FK) and soft-delete pattern. Use Django signals to seed default categories on user creation. Register all models in admin for visibility.

**Model relationships:**
```
User (django.contrib.auth)
  └── Category (name, is_deleted)
        ├── Budget (category FK, month, amount)
        └── Expense (category FK, amount, date, description)
```

---

## Phase 1: Create budget app & define models

### Overview

Scaffold the `budget` Django app and define Category, Budget, and Expense models with proper relationships and soft-delete support.

### Changes Required:

#### 1. Create Django app

**Command:** `python manage.py startapp budget`

**Intent:** Scaffold the budget app with standard Django structure (models.py, admin.py, apps.py, etc.).

#### 2. Define models

**File:** `budget/models.py`

**Intent:** Define three models — Category (user-owned, named), Budget (category + month + amount), Expense (category + amount + date + optional description). All include `user` FK, `is_deleted` boolean, and `created_at`/`updated_at` timestamps.

**Contract:**
- `Category`: `user` (FK to User), `name` (CharField max 100), `is_deleted` (BooleanField default False), `created_at`, `updated_at`
- `Budget`: `user` (FK), `category` (FK to Category), `month` (DateField — first day of month), `amount` (DecimalField max_digits=10, decimal_places=2), `is_deleted`, `created_at`, `updated_at`. Unique constraint on (user, category, month).
- `Expense`: `user` (FK), `category` (FK to Category), `amount` (DecimalField), `date` (DateField), `description` (CharField max 255, blank=True), `is_deleted`, `created_at`, `updated_at`

#### 3. Register app in settings

**File:** `coinductor/settings.py`

**Intent:** Add `'budget'` to INSTALLED_APPS so Django recognizes the app and its models.

**Contract:** Append `'budget'` to the INSTALLED_APPS list.

### Success Criteria:

#### Automated Verification:

- App structure exists: `ls budget/models.py budget/admin.py budget/apps.py`
- Models import without error: `python -c "from budget.models import Category, Budget, Expense"`
- Settings updated: `grep -q "'budget'" coinductor/settings.py`

#### Manual Verification:

- Review models.py to confirm field types and relationships match the contract

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Generate and apply migrations

### Overview

Generate Django migrations for the new models and apply them to the database. Register models in admin for inspection.

### Changes Required:

#### 1. Generate migrations

**Command:** `python manage.py makemigrations budget`

**Intent:** Create initial migration file for Category, Budget, Expense models.

**Contract:** Migration file created at `budget/migrations/0001_initial.py` with CreateModel operations for all three models.

#### 2. Apply migrations

**Command:** `python manage.py migrate`

**Intent:** Apply migrations to SQLite database (dev) — creates budget_category, budget_budget, budget_expense tables.

#### 3. Register models in admin

**File:** `budget/admin.py`

**Intent:** Register Category, Budget, Expense in Django admin with useful list displays for debugging.

**Contract:** 
- `CategoryAdmin`: list_display = (name, user, is_deleted, created_at)
- `BudgetAdmin`: list_display = (category, month, amount, user, is_deleted)
- `ExpenseAdmin`: list_display = (category, amount, date, user, is_deleted)

### Success Criteria:

#### Automated Verification:

- Migration exists: `ls budget/migrations/0001_initial.py`
- Migrations applied: `python manage.py showmigrations budget` shows `[X] 0001_initial`
- No pending migrations: `python manage.py makemigrations --check` exits 0
- Tables created: `python manage.py dbshell` + `.tables` shows budget_* tables (SQLite)

#### Manual Verification:

- Django admin at `/admin/` shows Category, Budget, Expense models
- Can create a test Category via admin

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Seed default categories on user signup

### Overview

Hook into user creation to automatically seed default categories (Food, Transport, Entertainment, etc.) so new users have a non-empty starting state.

### Changes Required:

#### 1. Define default categories

**File:** `budget/models.py` (or `budget/constants.py`)

**Intent:** Define the list of default category names to seed for new users.

**Contract:** `DEFAULT_CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Health', 'Other']`

#### 2. Create signal handler

**File:** `budget/signals.py`

**Intent:** Define a `post_save` signal handler for User model that creates default categories when a new user is created (`created=True`).

**Contract:** 
- Function `create_default_categories(sender, instance, created, **kwargs)`
- On `created=True`, bulk-create Category objects for each name in DEFAULT_CATEGORIES, owned by `instance` (the new user)

#### 3. Connect signal in app config

**File:** `budget/apps.py`

**Intent:** Import and connect the signal in the `ready()` method of BudgetConfig.

**Contract:** Override `ready(self)` to import `budget.signals`.

### Success Criteria:

#### Automated Verification:

- Signal file exists: `ls budget/signals.py`
- Apps.py has ready method: `grep -q "def ready" budget/apps.py`

#### Manual Verification:

- Create new user via `/signup/` → user has 7 default categories in admin
- Existing users are unaffected (no categories retroactively added)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: Final verification

### Overview

Comprehensive verification that all models, migrations, and seeding work correctly end-to-end.

### Changes Required:

No code changes — verification only.

### Success Criteria:

#### Automated Verification:

- All tests pass: `python manage.py test budget` (if tests exist)
- Server starts without errors: `python manage.py runserver` (quick check)
- Type check (if configured): ensure no import errors

#### Manual Verification:

- Create a new user via signup → confirm 7 default categories appear in admin
- Create a Budget entry in admin (link to category, set month, amount)
- Create an Expense entry in admin (link to category, set amount, date)
- Verify soft-delete: set `is_deleted=True` on a category, confirm it persists

---

## Testing Strategy

### Unit Tests:

- Model creation: Category, Budget, Expense can be created with valid data
- Unique constraint: Budget(user, category, month) rejects duplicates
- Soft delete: `is_deleted=True` doesn't remove record from DB

### Integration Tests:

- Signal: New user creation triggers category seeding
- Admin: Models appear and are editable

### Manual Testing Steps:

1. Sign up as new user → check admin for 7 default categories
2. Create Budget for one category → verify in admin
3. Create Expense → verify in admin
4. Delete expense (soft) → confirm `is_deleted=True`, record still in DB

## Performance Considerations

- Category seeding uses `bulk_create` for efficiency (single INSERT)
- Budget unique constraint (user, category, month) adds a DB index — fast lookups for S-01
- Expense queries will filter by user + date range — consider index on (user, date) if S-01 is slow

## Migration Notes

- First migration (`0001_initial`) creates all tables fresh — no data migration needed
- If deployed to Railway (PostgreSQL), run `python manage.py migrate` on first deploy
- Existing users (if any in production) won't get default categories — consider a data migration if needed later

## References

- PRD: `context/foundation/prd.md` — FR-003 (categories), FR-004 (expenses), Business Logic section
- Roadmap: `context/foundation/roadmap.md` — F-02 definition
- Tech stack: `context/foundation/tech-stack.md` — Django ORM, migrations

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Create budget app & define models

#### Automated

- [x] 1.1 App structure exists (budget/models.py, budget/admin.py, budget/apps.py) — b27772d
- [x] 1.2 Models import without error — b27772d
- [x] 1.3 Settings updated with 'budget' in INSTALLED_APPS — b27772d

#### Manual

- [ ] 1.4 Review models.py confirms field types and relationships match contract

### Phase 2: Generate and apply migrations

#### Automated

- [x] 2.1 Migration file exists (budget/migrations/0001_initial.py)
- [x] 2.2 Migrations applied (showmigrations shows [X])
- [x] 2.3 No pending migrations (makemigrations --check exits 0)
- [x] 2.4 Tables created in database

#### Manual

- [ ] 2.5 Django admin shows Category, Budget, Expense models
- [ ] 2.6 Can create a test Category via admin

### Phase 3: Seed default categories on user signup

#### Automated

- [ ] 3.1 Signal file exists (budget/signals.py)
- [ ] 3.2 Apps.py has ready method

#### Manual

- [ ] 3.3 New user signup creates 7 default categories
- [ ] 3.4 Existing users unaffected

### Phase 4: Final verification

#### Automated

- [ ] 4.1 Server starts without errors

#### Manual

- [ ] 4.2 Full end-to-end test: signup → categories → budget → expense → soft delete
