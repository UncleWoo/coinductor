# Minimal Auth Scaffold Implementation Plan

## Overview

Set up Django's built-in authentication system with email/password signup and login, styled with Tailwind CSS. This foundation unlocks S-01 (dashboard requires authenticated user context). Users will be auto-logged in after successful signup and redirected to the home page.

## Current State Analysis

The Django project has authentication infrastructure partially in place but no user-facing auth flow:

### What Exists:
- **Django auth configured**: `django.contrib.auth` in INSTALLED_APPS (settings.py:37)
- **Middleware in place**: `AuthenticationMiddleware` configured (settings.py:50)
- **Password validation**: All four Django validators configured (settings.py:102-115)
- **Static files**: WhiteNoise middleware configured (settings.py:46), STATIC_URL and STATIC_ROOT set (settings.py:133-134)
- **Database**: SQLite for development, PostgreSQL config ready for Railway deployment (settings.py:78-96)

### What's Missing:
- No authentication views (signup, login, logout)
- No authentication URLs configured
- No templates directory structure
- No CSS framework integration
- No auth-related settings (LOGIN_URL, LOGIN_REDIRECT_URL, etc.)
- No navigation or user state indication in UI

### Key Discoveries:
- Project uses Django's default User model (no custom AUTH_USER_MODEL) — signup view will use username field for email per user's decision
- TEMPLATES 'DIRS' is empty (settings.py:60) — need to create project-level templates directory
- No Node.js dependencies yet — clean slate for Tailwind integration
- urls.py (line 25) only has a plain home view and admin route — plenty of space for auth URLs

## Desired End State

After this plan is complete:

1. **User can sign up**: Visit `/signup/`, fill email (stored as username) + password, auto-login, redirect to home
2. **User can log in**: Visit `/login/`, authenticate, redirect to home
3. **User can log out**: Click logout link, confirm, redirect to login page
4. **UI reflects auth state**: Navigation shows "Login | Sign Up" for anonymous users, "Logout" for authenticated users
5. **Professional appearance**: All auth pages styled with Tailwind CSS using utility-first classes
6. **Build process works**: `npm run build` compiles Tailwind, ready for local dev and Railway deployment

### Verification:
- Anonymous user visiting `/` sees "Login | Sign Up" links
- Signup flow creates user in database, logs them in, shows their username in nav
- Login with wrong credentials shows error, correct credentials succeeds
- Logout removes session, returns to login page
- All pages render with Tailwind styling (responsive, clean forms)

## What We're NOT Doing

- Email verification (out of scope for MVP per PRD FR-001 Socrates note)
- Password reset flow (can be added post-MVP)
- OAuth/social login (explicitly deferred per PRD)
- Custom User model with email as USERNAME_FIELD (using Django default is simpler)
- Email backend configuration (no emails needed for MVP)
- Rate limiting or CAPTCHA (not in PRD scope)
- Profile pages or user settings (separate feature)
- Remember me / persistent sessions (Django defaults are sufficient)

## Implementation Approach

**Leverage Django's batteries-included philosophy**: Use built-in `LoginView`, `LogoutView`, and `UserCreationForm` instead of custom implementations. This gives us password validation, CSRF protection, and session management for free.

**Tailwind via npm + CLI**: Fastest production-ready approach for 3-week MVP. CDN is 5x larger; django-tailwind adds unnecessary dependencies. We compile once before deployment (no Node.js runtime needed in production).

**Progressive enhancement**: Phase 1 sets up styling infrastructure, Phase 2 wires auth logic, Phase 3 makes it look good, Phase 4 integrates with the rest of the app. Each phase is independently testable.

**Username-as-email convention**: Store email in the `username` field (Django default User model). Simpler than custom User model, sufficient for MVP. Forms will label it "Email" but save to `username` behind the scenes.

## Phase 1: Tailwind CSS Setup & Base Template

### Overview

Install Tailwind CSS tooling, configure static files, and create a base template with navigation structure. This establishes the styling foundation for all auth pages.

### Changes Required:

#### 1. Railway Buildpack Configuration (if deploying to Railway)

**File**: `railway.json` (new, optional)

**Intent**: Explicitly configure Railway to use both Python and Node.js buildpacks, preventing auto-detection failures during deployment.

**Contract**: Creates `railway.json` with:
```json
{
  "build": {
    "builder": "NIXPACKS"
  }
}
```

Railway's Nixpacks builder auto-detects both Python (from requirements.txt) and Node.js (from package.json) and makes both available in the build environment. This ensures `npm` commands in Procfile will work.

**Verification**: Run `railway run npm --version` after creating package.json to confirm Node.js is available in Railway environment.

#### 2. Node.js Dependency Setup

**File**: `package.json` (new)

**Intent**: Initialize npm project and install Tailwind CSS with required build tools for compiling utility classes into production CSS. This file also triggers Railway's Node.js buildpack detection.

**Contract**: Creates `package.json` with scripts `build` and `watch`, installs `tailwindcss`, `postcss`, `autoprefixer` as dev dependencies.

#### 3. Tailwind Configuration

**File**: `tailwind.config.js` (new)

**Intent**: Configure Tailwind to scan Django templates for class names, enabling tree-shaking to keep compiled CSS small.

**Contract**:
```javascript
module.exports = {
  content: [
    './coinductor/templates/**/*.html',
    './*/templates/**/*.html',
  ],
  theme: { extend: {} },
  plugins: [],
}
```

**File**: `postcss.config.js` (new)

**Intent**: Configure PostCSS to process Tailwind directives and add vendor prefixes for browser compatibility.

**Contract**: Standard PostCSS config with `tailwindcss` and `autoprefixer` plugins.

#### 4. Tailwind Source CSS

**File**: `static/css/input.css` (new)

**Intent**: Define Tailwind layers that will be processed into the final CSS bundle.

**Contract**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### 5. Static Files Configuration

**File**: `coinductor/settings.py`

**Intent**: Tell Django where to find source static files before WhiteNoise serves them in production.

**Contract**: Add after line 134:
```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

#### 6. Base Template with Navigation

**File**: `coinductor/templates/base.html` (new)

**Intent**: Create reusable HTML skeleton with Tailwind styles, responsive navigation, and content block for child templates to extend.

**Contract**: Includes `{% load static %}`, links compiled CSS from `static/css/output.css`, defines `{% block content %}`, navigation shows auth state with `{% if user.is_authenticated %}`.

#### 7. Update Settings for Template Directory

**File**: `coinductor/settings.py`

**Intent**: Point Django template loader at the new project-level templates directory.

**Contract**: Update line 60 from `'DIRS': []` to `'DIRS': [BASE_DIR / 'coinductor' / 'templates']`.

### Success Criteria:

#### Automated Verification:

- Railway buildpack ready (if deploying): `railway run npm --version` succeeds (skip if Railway not set up yet)
- Tailwind installs: `npm install` completes without errors
- CSS compiles: `npm run build` generates `static/css/output.css`
- Static files collect: `python manage.py collectstatic --noinput` succeeds
- Server starts: `python manage.py runserver` runs without errors
- Base template loads: `curl http://localhost:8000/` returns HTML with Tailwind classes

#### Manual Verification:

- Visit `http://localhost:8000/` in browser — page renders with styled navigation
- Inspect page source — `<link>` tag points to `/static/css/output.css`
- Navigation shows placeholder links (Login | Sign Up) — proper structure in place
- Responsive check: resize browser window, navigation adapts (mobile menu if implemented)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Authentication URLs & Views

### Overview

Configure Django's built-in authentication URLs and create a custom signup view. Set redirect URLs for login/logout flows.

### Changes Required:

#### 1. Authentication URL Configuration

**File**: `coinductor/urls.py`

**Intent**: Wire Django's built-in LoginView and LogoutView to `/login/` and `/logout/`, plus add signup URL route.

**Contract**: Add after line 18:
```python
from django.contrib.auth import views as auth_views
from . import views  # for signup view
```

Add to urlpatterns before admin route:
```python
path('signup/', views.signup, name='signup'),
path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
```

#### 2. Signup View

**File**: `coinductor/views.py` (new)

**Intent**: Create function-based signup view that uses UserCreationForm, labels username field as "Email", validates email format server-side, auto-logs in user after successful registration, and redirects to home.

**Contract**: Function signature `def signup(request)`. On POST: if `form.is_valid()`, validate username is valid email format using Django's `EmailValidator`. If validation fails, add form error via `form.add_error('username', 'Enter a valid email address.')` and re-render form. If valid: `form.save()`, `login(request, user)`, `redirect('home')`. On GET or invalid POST: render `registration/signup.html` with form context.

Import required: `from django.core.validators import EmailValidator` and `from django.core.exceptions import ValidationError`.

#### 3. Authentication Settings

**File**: `coinductor/settings.py`

**Intent**: Configure where Django redirects users after login/logout actions.

**Contract**: Add after line 149 (after DEFAULT_AUTO_FIELD):
```python
# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
```

### Success Criteria:

#### Automated Verification:

- URL routing works: `python manage.py show_urls` (if django-extensions installed) or manual curl tests succeed
- No import errors: `python manage.py check` passes
- Migrations up to date: `python manage.py migrate` reports no pending migrations (none expected — using default User model)

#### Manual Verification:

- Visit `http://localhost:8000/signup/` — renders signup form (may be unstyled, that's Phase 3)
- Visit `http://localhost:8000/login/` — renders login form
- Visit `http://localhost:8000/logout/` — renders logout confirmation
- Try to signup without templates (will error) — confirms views are wired correctly

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Authentication Templates

### Overview

Create Tailwind-styled templates for signup, login, and logout pages. These extend base.html and provide clean, responsive forms with error handling.

### Changes Required:

#### 1. Signup Template

**File**: `coinductor/templates/registration/signup.html` (new)

**Intent**: Render UserCreationForm with Tailwind styling, label username as "Email", show field errors, and provide link to login for existing users.

**Contract**: Extends `base.html`, uses `{% block content %}`. Form fields styled with Tailwind utility classes (e.g., `class="border rounded px-3 py-2"`). Submit button labeled "Sign Up". Link to login page below form.

#### 2. Login Template

**File**: `coinductor/templates/registration/login.html` (new)

**Intent**: Render Django's built-in login form with Tailwind styling, show authentication errors, and provide link to signup for new users.

**Contract**: Extends `base.html`, form posts to `{% url 'login' %}`. Username field relabeled "Email" via template (not form modification). Remember me checkbox optional. Link to signup below form.

#### 3. Logout Confirmation Template

**File**: `coinductor/templates/registration/logged_out.html` (new)

**Intent**: Confirm successful logout and offer link back to login or home page.

**Contract**: Extends `base.html`, simple message "You have been logged out." with styled link to login page.

#### 4. Form Error Styling

**File**: `coinductor/templates/base.html`

**Intent**: Add Django messages framework display area for form errors and success messages.

**Contract**: Add messages block in base template (before `{% block content %}`):
```django
{% if messages %}
  <div class="container mx-auto px-4 py-2">
    {% for message in messages %}
      <div class="bg-{{ message.tags }}-100 border border-{{ message.tags }}-400 text-{{ message.tags }}-700 px-4 py-3 rounded">
        {{ message }}
      </div>
    {% endfor %}
  </div>
{% endif %}
```

### Success Criteria:

#### Automated Verification:

- Templates load without errors: `python manage.py check --deploy` passes template validation
- CSS classes compile: `npm run build` includes all Tailwind classes used in templates (check output.css size increases)

#### Manual Verification:

- Visit `/signup/` — form renders with clean Tailwind styling, "Email" and "Password" fields visible
- Submit empty form — field-level errors appear with red styling
- Submit mismatched passwords — error displays clearly
- Submit valid signup — redirects to home, user is logged in
- Visit `/login/` — form styled consistently with signup
- Submit wrong credentials — error message appears
- Submit correct credentials — redirects to home
- Click logout — confirmation page appears, session cleared

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: Integration & Testing

### Overview

Update the home view to show authenticated user state, finalize navigation links, and test the complete authentication flow end-to-end.

### Changes Required:

#### 1. Update Home View

**File**: `coinductor/urls.py`

**Intent**: Replace plain-text HttpResponse home view with template-rendered view that shows auth state.

**Contract**: Change line 21-22 from:
```python
def home(request):
    return HttpResponse("Coinductor is running! 🚀")
```
to:
```python
def home(request):
    return render(request, 'home.html')
```

Add import at top: `from django.shortcuts import render` (update existing import line).

#### 2. Home Template

**File**: `coinductor/templates/home.html` (new)

**Intent**: Show welcome message that changes based on auth state — displays username if logged in, encourages signup if anonymous.

**Contract**: Extends `base.html`. Uses `{% if user.is_authenticated %}` to show personalized greeting with username. For anonymous users, shows call-to-action to sign up.

#### 3. Navigation Links

**File**: `coinductor/templates/base.html`

**Intent**: Replace placeholder navigation with real auth links that reflect user state.

**Contract**: Update navigation section to show:
- Authenticated users: "Welcome, {{ user.username }} | Logout"
- Anonymous users: "Login | Sign Up"

Links use `{% url 'login' %}`, `{% url 'signup' %}`, `{% url 'logout' %}`.

#### 4. .gitignore Updates

**File**: `.gitignore`

**Intent**: Prevent Node.js artifacts and compiled CSS from cluttering version control.

**Contract**: Add to `.gitignore`:
```
node_modules/
npm-debug.log
static/css/output.css
```

(Note: Some teams commit `output.css` for simpler deployment — decide based on CI/CD setup. For Railway with build step, exclude it.)

#### 5. Procfile Update for Deployment

**File**: `Procfile`

**Intent**: Ensure Tailwind CSS builds during Railway deployment before server starts.

**Contract**: Update to:
```
release: npm install && npm run build && python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn coinductor.wsgi
```

### Success Criteria:

#### Automated Verification:

- All URLs resolve: Test GET requests to `/`, `/signup/`, `/login/`, `/logout/`
- Home page loads: `curl http://localhost:8000/` returns HTML with user state
- Linting passes: `python manage.py check --deploy` reports no issues
- Static files collected: `python manage.py collectstatic` completes successfully

#### Manual Verification:

- **Complete auth flow (anonymous → signed up → logged out → logged in)**:
  1. Visit `/` as anonymous — navigation shows "Login | Sign Up"
  2. Click "Sign Up" → form appears
  3. Fill email (e.g., test@example.com) and password → submit
  4. Redirected to `/` — navigation now shows "Welcome, test@example.com | Logout"
  5. Click "Logout" → confirmation page appears
  6. Redirected to `/login/` — navigation shows "Login | Sign Up" again
  7. Click "Login" → fill same credentials → submit
  8. Redirected to `/` — logged in again
- **Error handling**:
  - Signup with existing username → error message appears
  - Login with wrong password → error message appears
  - Visit `/admin/` → redirects to `/admin/login/` (Django admin still works)
- **Responsive design**: Test on mobile viewport (350px width) — navigation remains usable

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Testing Strategy

### Unit Tests:

No custom business logic in this phase — leveraging Django's tested auth system. Consider adding tests for:
- Signup view creates user correctly
- Signup view auto-logs in user
- Username field accepts email format

(Tests can be added post-implementation if needed — not blocking for MVP.)

### Integration Tests:

- Full signup → login → logout flow (manual verification covers this)
- Navigation state changes based on auth status
- Redirect URLs work as configured

### Manual Testing Steps:

1. **Fresh signup flow**:
   - Clear browser cookies/use incognito
   - Visit home page → click Sign Up
   - Fill form → submit
   - Verify auto-login and redirect to home
   - Verify username appears in navigation

2. **Login with existing account**:
   - Log out
   - Visit login page
   - Enter valid credentials → verify redirect
   - Enter invalid credentials → verify error message

3. **Logout flow**:
   - Click logout link
   - Verify confirmation page
   - Verify redirect to login
   - Verify session cleared (cannot access protected pages)

4. **Edge cases**:
   - Try duplicate email signup → expect error
   - Submit empty forms → expect field validation errors
   - Check CSRF protection (form without token should fail)

5. **Visual/UX checks**:
   - All forms render cleanly with Tailwind styling
   - Error messages are readable and well-positioned
   - Navigation links are clickable and styled correctly
   - Responsive behavior works on mobile (test at 375px width)

## Performance Considerations

- **Tailwind CSS size**: Compiled output.css should be ~10-20KB (gzipped ~5KB) — much smaller than CDN's 75KB
- **Static file caching**: WhiteNoise handles this automatically with `CompressedManifestStaticFilesStorage`
- **Session storage**: Django's default database session backend is sufficient for MVP scale (PRD target: medium users, low QPS)
- **Password hashing**: Django's PBKDF2 hasher with 390,000 iterations (settings.py defaults) — secure and fast enough

No performance optimizations needed for auth at this stage. The bottleneck will be business logic (budget calculations), not auth.

## Migration Notes

Not applicable — using Django's default User model, no database migrations needed beyond initial `python manage.py migrate`.

If switching to custom User model post-MVP, that's a separate change requiring data migration. For now, username-as-email is sufficient.

## References

- PRD: `context/foundation/prd.md` (FR-001, FR-002, §Access Control)
- Roadmap: `context/foundation/roadmap.md` (F-01)
- Tech Stack: `context/foundation/tech-stack.md` (Django 6.0.6, uv package manager)
- Django Auth Docs: https://docs.djangoproject.com/en/6.0/topics/auth/
- Tailwind CSS Docs: https://tailwindcss.com/docs/installation

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Tailwind CSS Setup & Base Template

#### Automated

- [x] 1.1 Railway buildpack ready (if deploying): `railway run npm --version` succeeds — f79b225
- [x] 1.2 Tailwind installs: `npm install` completes without errors — f79b225
- [x] 1.3 CSS compiles: `npm run build` generates `static/css/output.css` — f79b225
- [x] 1.4 Static files collect: `python manage.py collectstatic --noinput` succeeds — f79b225
- [x] 1.5 Server starts: `python manage.py runserver` runs without errors — f79b225
- [x] 1.6 Base template loads: `curl http://localhost:8000/` returns HTML with Tailwind classes — f79b225

#### Manual

- [x] 1.7 Visit home in browser — page renders with styled navigation — f79b225
- [x] 1.8 Inspect page source — link tag points to `/static/css/output.css` — f79b225
- [x] 1.9 Navigation shows placeholder links (Login | Sign Up) — f79b225
- [x] 1.10 Responsive check: resize browser window, navigation adapts — f79b225

### Phase 2: Authentication URLs & Views

#### Automated

- [x] 2.1 URL routing works: `python manage.py show_urls` (or manual curl tests) — 89b3fba
- [x] 2.2 No import errors: `python manage.py check` passes — 89b3fba
- [x] 2.3 Migrations up to date: `python manage.py migrate` reports no pending migrations — 89b3fba

#### Manual

- [x] 2.4 Visit `/signup/` — renders signup form — 89b3fba
- [x] 2.5 Visit `/login/` — renders login form — 89b3fba
- [x] 2.6 Visit `/logout/` — renders logout confirmation — 89b3fba

### Phase 3: Authentication Templates

#### Automated

- [x] 3.1 Templates load without errors: `python manage.py check --deploy` passes template validation — 7772b04
- [x] 3.2 CSS classes compile: `npm run build` includes all Tailwind classes used in templates — 7772b04

#### Manual

- [x] 3.3 Visit `/signup/` — form renders with clean Tailwind styling — 7772b04
- [x] 3.4 Submit empty form — field-level errors appear with red styling — 7772b04
- [x] 3.5 Submit mismatched passwords — error displays clearly — 7772b04
- [x] 3.6 Submit valid signup — redirects to home, user is logged in — 7772b04
- [x] 3.7 Visit `/login/` — form styled consistently with signup — 7772b04
- [x] 3.8 Submit wrong credentials — error message appears — 7772b04
- [x] 3.9 Submit correct credentials — redirects to home — 7772b04
- [x] 3.10 Click logout — confirmation page appears, session cleared — 7772b04

### Phase 4: Integration & Testing

#### Automated

- [x] 4.1 All URLs resolve: Test GET requests to `/`, `/signup/`, `/login/`, `/logout/` — b18c8f0
- [x] 4.2 Home page loads: `curl http://localhost:8000/` returns HTML with user state — b18c8f0
- [x] 4.3 Linting passes: `python manage.py check --deploy` reports no issues — b18c8f0
- [x] 4.4 Static files collected: `python manage.py collectstatic` completes successfully — b18c8f0

#### Manual

- [x] 4.5 Complete auth flow: anonymous → signup → logout → login — b18c8f0
- [x] 4.6 Error handling: duplicate signup shows error — b18c8f0
- [x] 4.7 Error handling: wrong login password shows error — b18c8f0
- [x] 4.8 Django admin still works: `/admin/` redirects to login — b18c8f0
- [x] 4.9 Responsive design: test on mobile viewport (350px width) — b18c8f0
