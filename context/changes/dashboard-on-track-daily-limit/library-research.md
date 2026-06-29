# S-01 Library Research: Dashboard with On-Track Status + Daily Limit

**Date:** 2026-06-29  
**Change ID:** dashboard-on-track-daily-limit  
**PRD refs:** US-01, FR-005, FR-006, FR-007  
**Stack:** Django 6.0.6, Python 3.13, SQLite, uv

## S-01 Requirements Summary

Build a dashboard showing:
- On-track status (yes/no, green/red indicator)
- Remaining budget
- Days left in month
- Daily limit = `remaining_money / remaining_days`

---

## Compatible Libraries Research

### 1. Core Framework (Already in Stack)

| Library | ID | Description | Snippets | Score | Recommendation |
|---------|-----|-------------|----------|-------|----------------|
| **Django 6.0** | `/websites/djangoproject_en_6_0` | High-level Python web framework | 10,722 | 83.36 | ✅ **Already in stack** - use built-in views, templates, ORM |

**Why sufficient:** Django's built-in class-based views, template system, and ORM are adequate for the S-01 dashboard. No additional framework needed.

---

### 2. Date Calculation Libraries

| Library | ID | Description | Snippets | Score | Recommendation |
|---------|-----|-------------|----------|-------|----------------|
| **python-dateutil** | `/dateutil/dateutil` | Powerful datetime extensions (relative deltas, parsing) | 162 | 74.5 | ✅ **Recommended** |

**Use case for S-01:**
- Calculate remaining days in month: `relativedelta` to find month end
- Handle edge cases (leap years, month boundaries)

**Alternative:** Python's built-in `calendar.monthrange()` may suffice for simple "days left" calculation without adding a dependency.

```python
# Built-in approach (no extra dependency)
import calendar
from datetime import date

today = date.today()
_, days_in_month = calendar.monthrange(today.year, today.month)
remaining_days = days_in_month - today.day + 1  # +1 to include today
```

**Verdict:** Start with built-in `calendar` module. Add `python-dateutil` only if more complex date logic emerges.

---

### 3. Dynamic UI Updates (Optional)

| Library | ID | Description | Snippets | Score | Recommendation |
|---------|-----|-------------|----------|-------|----------------|
| **HTMX** | `/bigskysoftware/htmx` | AJAX from HTML attributes | 1,937 | 84.18 | ⚠️ **Optional for S-01** |
| **django-htmx** | `/adamchainz/django-htmx` | Django utilities for HTMX integration | 109 | 75.53 | ⚠️ **Optional for S-01** |

**Use case for S-01:**
- S-01 is a read-only dashboard (no dynamic updates needed)
- HTMX becomes valuable for **S-02** (expense entry with instant recalculation)

**Verdict:** Defer HTMX to S-02. S-01 can use standard Django template rendering.

---

### 4. CSS / Styling Libraries

| Library | ID | Description | Snippets | Score | Recommendation |
|---------|-----|-------------|----------|-------|----------------|
| **TailwindCSS** | (various) | Utility-first CSS framework | varies | varies | ✅ **Recommended** |

**Use case for S-01:**
- Status indicators (green/red on-track badge)
- Card layouts for budget display
- Responsive design (mobile-first per PRD guardrail)

**Verdict:** TailwindCSS via CDN is lightweight and sufficient for MVP. No build step required.

```html
<!-- CDN approach for MVP -->
<script src="https://cdn.tailwindcss.com"></script>
```

---

### 5. Form Libraries (For future slices)

| Library | ID | Description | Snippets | Score | Recommendation |
|---------|-----|-------------|----------|-------|----------------|
| **django-crispy-forms** | `/django-crispy-forms/django-crispy-forms` | DRY form rendering | 345 | 90.5 | ⚠️ **Defer to S-02/S-03** |
| **crispy-tailwind** | `/django-crispy-forms/crispy-tailwind` | Tailwind template pack for crispy | 511 | - | ⚠️ **Defer to S-02/S-03** |

**Use case:** Not needed for S-01 (read-only dashboard). Becomes relevant for:
- S-02: Expense entry form
- S-03: Budget category setup form

**Verdict:** Defer installation until S-02 planning.

---

## Recommended Stack for S-01

### Must Install
| Library | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| *(none)* | - | S-01 can be built with Django built-ins | - |

### CDN Only (No Install)
| Library | Purpose | CDN |
|---------|---------|-----|
| TailwindCSS | Styling | `<script src="https://cdn.tailwindcss.com"></script>` |

### Optional (Evaluate During Implementation)
| Library | Purpose | Install Command |
|---------|---------|-----------------|
| python-dateutil | Complex date calculations | `uv pip install python-dateutil` |

---

## Implementation Notes

### Daily Limit Calculation (Core Logic)
```python
# services/budget.py
from datetime import date
import calendar

def calculate_daily_limit(user) -> dict:
    today = date.today()
    _, days_in_month = calendar.monthrange(today.year, today.month)
    remaining_days = days_in_month - today.day + 1
    
    total_budget = Budget.objects.filter(user=user, month=today.month, year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Expense.objects.filter(user=user, date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    
    remaining_money = total_budget - total_spent
    daily_limit = remaining_money / remaining_days if remaining_days > 0 else 0
    on_track = remaining_money >= 0
    
    return {
        'daily_limit': daily_limit,
        'remaining_budget': remaining_money,
        'days_left': remaining_days,
        'on_track': on_track,
    }
```

### Dashboard Template (Minimal Example)
```html
<!-- templates/dashboard.html -->
<div class="p-4">
  <div class="rounded-lg p-6 {% if on_track %}bg-green-100{% else %}bg-red-100{% endif %}">
    <h2 class="text-xl font-bold">
      {% if on_track %}✅ On Track{% else %}❌ Over Budget{% endif %}
    </h2>
    <p class="text-3xl font-bold">{{ daily_limit|floatformat:2 }} zł/day</p>
    <p>{{ remaining_budget|floatformat:2 }} zł remaining • {{ days_left }} days left</p>
  </div>
</div>
```

---

## Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Django 6.0 (existing) | Already in stack, sufficient for S-01 |
| Date math | Python `calendar` built-in | Simple enough, no extra dependency |
| Styling | TailwindCSS CDN | Fast MVP, no build step |
| Dynamic updates | Defer to S-02 | S-01 is read-only |
| Forms | Defer to S-02/S-03 | S-01 has no forms |

**Bottom line:** S-01 requires **zero new library installations**. Django + TailwindCSS CDN is sufficient for the MVP dashboard.
