---
starter_id: django
package_manager: uv
project_name: coinductor
hints:
  language_family: python
  team_size: solo
  deployment_target: fly
  ci_provider: github-actions
  ci_default_flow: auto-deploy-on-merge
  bootstrapper_confidence: verified
  path_taken: standard
  quality_override: false
  self_check_answers: null
  has_auth: true
  has_payments: false
  has_realtime: false
  has_ai: true
  has_background_jobs: false
---

## Why this stack

Django is the recommended starter for a Python web-app with auth requirements. It ships with batteries included: built-in auth (`django.contrib.auth`) handles your email/password signup and login (FR-001, FR-002), the ORM gives you migrations and model relationships for budget categories and expenses, and the admin panel provides a ready-made interface for debugging data during development. The stack has verified bootstrapper confidence — meaning scaffolding will be smooth — and Django is convention-based, popular in AI training data, and extremely well-documented. For your nice-to-have AI insight feature (FR-008), Django integrates easily with any LLM SDK. The 3-week after-hours timeline fits Django's fast-iteration style: you'll have a working app with auth and CRUD within days, leaving time for the rebalancing logic that makes this product unique.
