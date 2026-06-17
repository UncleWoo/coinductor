---
bootstrapped_at: 2026-06-09T14:47:00Z
starter_id: django
starter_name: Django
project_name: coinductor
language_family: python
package_manager: uv
cwd_strategy: native-cwd
bootstrapper_confidence: verified
phase_3_status: ok
audit_command: pip-audit
---

## Hand-off

```yaml
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
```

### Why this stack

Django is the recommended starter for a Python web-app with auth requirements. It ships with batteries included: built-in auth (`django.contrib.auth`) handles your email/password signup and login (FR-001, FR-002), the ORM gives you migrations and model relationships for budget categories and expenses, and the admin panel provides a ready-made interface for debugging data during development. The stack has verified bootstrapper confidence — meaning scaffolding will be smooth — and Django is convention-based, popular in AI training data, and extremely well-documented. For your nice-to-have AI insight feature (FR-008), Django integrates easily with any LLM SDK. The 3-week after-hours timeline fits Django's fast-iteration style: you'll have a working app with auth and CRUD within days, leaving time for the rebalancing logic that makes this product unique.

## Pre-scaffold verification

| Signal             | Value                              | Severity | Notes                              |
| ------------------ | ---------------------------------- | -------- | ---------------------------------- |
| npm package        | not run                            | -        | non-JS starter                     |
| GitHub repo        | django/django last pushed 2026-06-09 | fresh    | from github.com API                |

## Scaffold log

**Resolved invocation**: `django-admin startproject coinductor .`
**Strategy**: native-cwd (scaffolds directly into the current directory)
**Exit code**: 0
**Pre-flight files-to-touch**: manage.py, coinductor/
**Files written by CLI**: 6 (manage.py, coinductor/__init__.py, coinductor/asgi.py, coinductor/settings.py, coinductor/urls.py, coinductor/wsgi.py)
**Pre-existing files preserved**: context/, .github/, idea-notes.md, pomysl.md
**Conflicts (.scaffold siblings)**: none
**.gitignore handling**: absent in scaffold

## Post-scaffold audit

**Tool**: pip-audit --format json
**Summary**: 0 CRITICAL, 0 HIGH, 0 MODERATE, 0 LOW
**Direct vs transitive**: not distinguished by this tool (all packages in venv audited)

No known vulnerabilities found in the dependency tree.

Packages audited:
- asgiref 3.11.1
- django 6.0.6
- sqlparse 0.5.5

## Hints recorded but not acted on

| Hint                       | Value                              |
| -------------------------- | ---------------------------------- |
| bootstrapper_confidence    | verified                           |
| quality_override           | false                              |
| path_taken                 | standard                           |
| self_check_answers         | null                               |
| team_size                  | solo                               |
| deployment_target          | fly                                |
| ci_provider                | github-actions                     |
| ci_default_flow            | auto-deploy-on-merge               |
| has_auth                   | true                               |
| has_payments               | false                              |
| has_realtime               | false                              |
| has_ai                     | true                               |
| has_background_jobs        | false                              |

## Next steps

Next: a future skill will set up agent context (CLAUDE.md, AGENTS.md). For now, your project is scaffolded and verified — happy hacking.

Useful manual steps in the meantime:
- `git init` (if you have not already) to start your own repo history.
- Review any `.scaffold` siblings the conflict policy created and decide which version of each file to keep.
- Address audit findings per your project's risk tolerance — the full breakdown is in this log.
- Create a `requirements.txt` or `pyproject.toml` to lock your dependencies: `uv pip freeze > requirements.txt`
- Run `python manage.py migrate` to set up the initial database.
- Run `python manage.py runserver` to start the development server.
