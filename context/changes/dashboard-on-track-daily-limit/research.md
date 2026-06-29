---
date: 2026-06-29T14:18:22+02:00
researcher: Copilot
git_commit: 2c39b58ad2c21e3fea2df709fdbe11283e5d08c7
branch: main
repository: UncleWoo/coinductor
topic: "S-01 Codebase Compatibility Review"
tags: [research, codebase, s-01, dashboard, compatibility]
status: complete
last_updated: 2026-06-29
last_updated_by: Copilot
---

# Research: S-01 Codebase Compatibility Review

**Date**: 2026-06-29T14:18:22+02:00  
**Researcher**: Copilot  
**Git Commit**: 2c39b58ad2c21e3fea2df709fdbe11283e5d08c7  
**Branch**: main  
**Repository**: UncleWoo/coinductor

## Research Question

Is the "zero-install" approach recommended in the external library research (exa-search-results.md, library-research.md) compatible with the existing Coinductor codebase for implementing S-01 (dashboard with on-track status + daily limit)?

## Summary

**✅ FULLY COMPATIBLE** — The external research's "zero-install" recommendation aligns perfectly with the existing codebase. The project already has:

- TailwindCSS 3.4.17 with build pipeline (not CDN as suggested — **better**)
- Django 6.0.6 templates with established patterns
- Authentication scaffolding ready (F-01 partially complete)
- No conflicting dependencies or patterns

**Key adjustment**: Use the existing TailwindCSS build setup instead of CDN.

## Detailed Findings

### 1. Django Configuration

| Finding | Value | File:Line |
|---------|-------|-----------|
| Django version | 6.0.6 | `coinductor/settings.py:4` |
| Template directory | `coinductor/templates/` | `coinductor/settings.py:83` |
| Static files | WhiteNoise + `static/` dir | `coinductor/settings.py:156-168` |
| Auth backend | `django.contrib.auth` (default User) | `coinductor/settings.py:60` |
| Database | SQLite (dev) / PostgreSQL (prod) | `coinductor/settings.py:101-119` |

**Compatibility**: ✅ Standard Django setup, no conflicts with S-01 requirements.

### 2. Existing Template Patterns

| Pattern | Status | Reference |
|---------|--------|-----------|
| Base template inheritance | ✅ Exists | `coinductor/templates/base.html` |
| TailwindCSS styling | ✅ Configured | `static/css/output.css` (compiled) |
| Form error handling | ✅ Pattern established | `registration/login.html`, `signup.html` |
| Content block | ✅ `{% block content %}` | `base.html` |

**Templates found**:
- `base.html` — master layout with nav, messages, content block
- `home.html` — current home page (placeholder for dashboard)
- `registration/login.html`, `signup.html`, `logged_out.html` — auth templates

**Key patterns for S-01**:
```html
<!-- Status indicator pattern (from existing button styles) -->
bg-blue-600 hover:bg-blue-700  <!-- primary action -->
bg-green-100 text-green-800    <!-- success state (use for on-track) -->
bg-red-100 text-red-800        <!-- error state (use for over-budget) -->
```

### 3. Authentication State

| Component | Status | Reference |
|-----------|--------|-----------|
| Auth middleware | ✅ Configured | `settings.py:73` |
| Login/logout views | ✅ Working | `urls.py:25-26`, `views.py:28-33` |
| Signup flow | ✅ Working | `views.py:8-25` |
| `@login_required` | ❌ Not used | Template-level auth checks only |
| LOGIN_REDIRECT_URL | ✅ Points to `'home'` | `settings.py:179` |

**S-01 implication**: Dashboard view should use `@login_required` decorator to protect budget data. Current `home` view is public.

### 4. Data Models State

| Model | Status | Blocker |
|-------|--------|---------|
| Budget | ❌ Not created | F-02 required |
| Expense | ❌ Not created | F-02 required |
| Category | ❌ Not created | F-02 required |
| User | ✅ Django default | Ready |

**S-01 blocker**: Models don't exist yet. Per roadmap, S-01 depends on F-02 (domain-models-migrations).

### 5. CSS/JS Stack

| Library | External Research | Actual Codebase | Delta |
|---------|-------------------|-----------------|-------|
| TailwindCSS | CDN recommended | **Build pipeline** (better) | ✅ Exceeds |
| PostCSS | Not mentioned | Configured | ✅ Bonus |
| AutoPrefixer | Not mentioned | Configured | ✅ Bonus |
| JavaScript | None needed | None present | ✅ Match |

**Build commands** (`package.json`):
```bash
npm run build   # Compile TailwindCSS
npm run watch   # Dev mode with hot reload
```

### 6. URL/View Patterns

| Pattern | Convention | Reference |
|---------|------------|-----------|
| View style | Function-based (FBV) | `views.py` |
| URL naming | `'home'`, `'login'`, `'signup'`, `'logout'` | `urls.py:23-26` |
| App structure | Monolithic (no apps yet) | Single `coinductor/` package |

**S-01 implication**: Dashboard can be added to existing `views.py` or a new `dashboard/` app can be created. Recommend keeping in `views.py` for MVP simplicity.

## Code References

- `coinductor/settings.py:58-65` — INSTALLED_APPS (Django defaults only)
- `coinductor/settings.py:80-93` — Template configuration
- `coinductor/settings.py:156-170` — Static files + WhiteNoise
- `coinductor/settings.py:178-180` — Auth redirect URLs
- `coinductor/urls.py:22-28` — All URL patterns
- `coinductor/views.py:36-37` — Current home view (dashboard placeholder)
- `coinductor/templates/base.html` — Master template with TailwindCSS
- `coinductor/templates/home.html` — Current home page
- `static/css/input.css` — TailwindCSS directives
- `tailwind.config.js` — TailwindCSS build config

## Architecture Insights

### Existing Conventions to Follow

1. **Template inheritance**: Extend `base.html`, use `{% block content %}`
2. **Styling**: Use existing TailwindCSS classes (slate, blue, green, red palette)
3. **Form errors**: Follow `registration/login.html` pattern for field validation
4. **Auth checks**: Template-level with `{% if user.is_authenticated %}`

### Recommended Adjustments for S-01

1. **Add `@login_required`** to dashboard view — don't rely solely on template checks
2. **Use existing build pipeline** — run `npm run build` after template changes, not CDN
3. **Keep FBV pattern** — match existing `home`, `signup`, `logout_view` conventions
4. **Add dashboard to home route** — replace current placeholder in `views.py:36-37`

### S-01 Implementation Sketch (Aligned with Codebase)

```python
# coinductor/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import date
import calendar

@login_required
def home(request):
    """Dashboard: on-track status + daily limit (S-01)"""
    today = date.today()
    _, days_in_month = calendar.monthrange(today.year, today.month)
    remaining_days = days_in_month - today.day + 1
    
    # TODO: Replace with actual model queries after F-02
    total_budget = 0  # Budget.objects.filter(...)
    total_spent = 0   # Expense.objects.filter(...)
    
    remaining_money = total_budget - total_spent
    daily_limit = remaining_money / remaining_days if remaining_days > 0 else 0
    
    return render(request, 'home.html', {
        'daily_limit': daily_limit,
        'remaining_budget': remaining_money,
        'days_left': remaining_days,
        'on_track': remaining_money >= 0,
    })
```

## Historical Context

No prior changes archived for S-01. This is the first research pass.

**Related roadmap items**:
- F-01 (`minimal-auth-scaffold`) — Partially complete (auth views exist)
- F-02 (`domain-models-migrations`) — **Blocker** for S-01 (no models yet)

## Compatibility Matrix

| External Research Recommendation | Codebase Reality | Verdict |
|----------------------------------|------------------|---------|
| Django 6.0 built-in views | ✅ Django 6.0.6 installed | Compatible |
| TailwindCSS via CDN | ✅ TailwindCSS 3.4.17 **build** | Better |
| Python `calendar` module | ✅ Python 3.13 | Compatible |
| No charts needed for S-01 | ✅ No chart libs installed | Compatible |
| Defer HTMX to S-02 | ✅ No HTMX installed | Aligned |
| Zero new dependencies | ✅ All needed libs present | Compatible |

## Open Questions

1. **F-02 completion status**: S-01 is blocked until Budget/Expense models exist. Should F-02 be planned first?
2. **Empty state UX**: What should dashboard show when user has no budget set? (PRD US-01 mentions "empty state guidance")
3. **App structure**: Keep dashboard in `coinductor/views.py` or create `dashboard/` app?

## Recommendations

### Immediate Actions

1. **Confirm F-02 is complete** before starting S-01 implementation
2. **Use existing TailwindCSS build** — ignore CDN suggestion from external research
3. **Add `@login_required`** to protect dashboard view

### For `/10x-plan dashboard-on-track-daily-limit`

The plan should include:
- View: `@login_required` FBV in `coinductor/views.py`
- Template: Update `home.html` with dashboard UI
- Business logic: `calculate_daily_limit()` service function
- Tests: Unit tests for daily limit calculation edge cases
- Build: `npm run build` after template changes

**Bottom line**: External research is valid and compatible. The codebase is ready for S-01 once F-02 (models) is complete.
