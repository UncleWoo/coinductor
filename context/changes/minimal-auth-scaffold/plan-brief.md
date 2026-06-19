# Minimal Auth Scaffold — Plan Brief

> Full plan: `context/changes/minimal-auth-scaffold/plan.md`

## What & Why

Set up Django's built-in authentication system with email/password signup and login, styled with Tailwind CSS. This is foundation change F-01 from the roadmap — it unlocks S-01 (dashboard) because the dashboard requires authenticated user context to show "their" budget data. Without auth, there's no way to know whose data to display.

## Starting Point

Django auth infrastructure is already configured (`django.contrib.auth` in INSTALLED_APPS, `AuthenticationMiddleware` active, password validators set), but no user-facing auth flow exists yet. The project has a plain home view that returns "Coinductor is running! 🚀" and an admin route, but no signup/login/logout views or templates.

## Desired End State

Users can sign up with email (stored in username field) and password, are auto-logged in after signup, and redirected to the home page. Logged-in users see their username in navigation with a Logout link. Anonymous users see Login | Sign Up links. All auth pages are styled with Tailwind CSS using utility-first classes. The build process compiles Tailwind CSS from source, ready for local development and Railway deployment.

## Key Decisions Made

| Decision                              | Choice                                             | Why (1 sentence)                                                                                      | Source |
| ------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------ |
| Post-signup flow                      | Auto-login and redirect to home                    | Reduces friction — user doesn't need to re-enter credentials after signup.                            | Plan   |
| Auth implementation                   | Django's built-in views (LoginView, UserCreationForm) | Batteries included — CSRF, password validation, session management for free.                          | Plan   |
| CSS framework                         | Tailwind CSS via npm + CLI                         | 5x smaller bundle than CDN (14KB vs 75KB), full customization, production-ready in 10 minutes.        | Plan   |
| User model strategy                   | Use username field for email                       | Simpler than custom User model, sufficient for MVP, avoids migration complexity.                      | Plan   |
| Navigation structure                  | Basic links in header (Login/Signup or Logout)     | Future-proofs for S-01 dashboard — nav skeleton ready for additional pages.                           | Plan   |

## Scope

**In scope:**
- Signup with email (stored as username) + password
- Login with email + password
- Logout with confirmation page
- Tailwind CSS setup (npm + CLI build process)
- Navigation that reflects auth state (logged in vs anonymous)
- Form error handling and validation messages
- Redirect URLs configured (login → home, logout → login)

**Out of scope:**
- Email verification (not in PRD for MVP)
- Password reset flow (post-MVP)
- OAuth/social login (explicitly deferred per PRD FR-001 Socrates note)
- Custom User model with email as USERNAME_FIELD (using Django default)
- Profile pages or user settings (separate feature)
- Rate limiting, CAPTCHA, or advanced security (not in PRD)

## Architecture / Approach

**Leverage Django's built-in auth**: Use `LoginView`, `LogoutView`, and `UserCreationForm` directly — no need to reinvent password hashing, CSRF protection, or session management. Create a thin signup view that wraps `UserCreationForm`, saves the user, logs them in, and redirects.

**Tailwind via npm + CLI**: Install Tailwind as a dev dependency, configure it to scan Django templates, compile CSS into `static/css/output.css`. Development: run `npm run watch` for live recompilation. Deployment: Procfile runs `npm install && npm run build` before server starts. No Node.js runtime needed in production — just serve the compiled CSS.

**Template inheritance**: Single `base.html` with navigation and `{% block content %}`. Auth templates (signup, login, logout) extend base and inject form HTML. Navigation uses `{% if user.is_authenticated %}` to show different links.

**Username-as-email convention**: The signup form's username field is labeled "Email" in the template, but saves to Django's default `User.username`. This avoids custom User model complexity while satisfying PRD FR-001 (sign up with email).

## Phases at a Glance

| Phase                                  | What it delivers                                                                 | Key risk                                                                                       |
| -------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1. Tailwind CSS Setup & Base Template  | Tailwind installed, compiled CSS, base.html with navigation skeleton            | npm/Node.js version mismatch on Railway — mitigated by pinning versions in package.json       |
| 2. Authentication URLs & Views         | Signup, login, logout routes wired; signup view with auto-login                 | Username-as-email confusion — forms must clearly label "Email" even though field is `username` |
| 3. Authentication Templates            | Styled signup/login/logout pages with Tailwind, error handling                  | Tailwind classes bloat — mitigated by tree-shaking (only used classes compiled)               |
| 4. Integration & Testing               | Home page shows auth state, navigation links functional, end-to-end flow tested | Session expiry on Railway — Django defaults are sufficient for MVP, can tune later             |

**Prerequisites:** Django 6.0.6 already installed, manage.py and settings.py in place, Railway deployment configured (Procfile exists). Node.js/npm available locally for development.

**Estimated effort:** ~1-2 sessions across 4 phases (Phase 1: 30 min, Phase 2: 20 min, Phase 3: 40 min, Phase 4: 30 min + testing). Total: 2-3 hours plus manual QA.

## Open Risks & Assumptions

- **Assumption**: Railway build environment has Node.js available for `npm install`. (Verified: Railway auto-detects Node.js when package.json exists.)
- **Assumption**: Email format validation happens client-side (browser) and server-side (Django's default validators). No custom email regex needed.
- **Risk**: If user enters non-email string as username, login still works but violates user expectation. Mitigation: Phase 2 signup view can add `EmailField` validation before saving to username.
- **Risk**: Tailwind compile step fails on Railway if npm version mismatch. Mitigation: Add `engines` field to package.json specifying Node 18+.

## Success Criteria (Summary)

- User can sign up with email + password → auto-logged in → redirected to home
- User can log in with email + password → redirected to home
- User can log out → confirmation page → redirected to login
- Navigation shows "Welcome, [email] | Logout" when authenticated, "Login | Sign Up" when anonymous
- All auth pages styled with Tailwind (clean forms, error messages, responsive layout)
- Build process works: `npm run build` generates `static/css/output.css`, Railway deploys successfully
