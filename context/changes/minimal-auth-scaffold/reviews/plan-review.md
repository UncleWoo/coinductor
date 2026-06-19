<!-- PLAN-REVIEW-REPORT -->
# Plan Review: Minimal Auth Scaffold Implementation Plan

- **Plan**: context/changes/minimal-auth-scaffold/plan.md
- **Mode**: Deep
- **Date**: 2026-06-19
- **Verdict**: SOUND (after fixes)
- **Findings**: 1 critical, 2 warnings, 0 observations

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| End-State Alignment | PASS |
| Lean Execution | PASS |
| Architectural Fitness | PASS |
| Blind Spots | PASS (after fix) |
| Plan Completeness | PASS (after fixes) |

## Grounding

5/5 paths ✓, 5/5 symbols ✓, brief↔plan ✓

## Findings

### F1 — Railway Node.js buildpack not verified

- **Severity**: ❌ CRITICAL
- **Impact**: 🔬 HIGH — architectural stakes; think carefully before deciding
- **Dimension**: Blind Spots
- **Location**: Phase 4 — Procfile Update for Deployment
- **Detail**: Plan modifies Procfile to add `npm install && npm run build` in the release phase (line 385), but never verifies that Railway has Node.js available. Railway auto-detects buildpacks based on files in repo—with only requirements.txt present now, it will use Python buildpack. Adding package.json triggers Node.js buildpack, BUT the plan doesn't explain this detection mechanism or what happens if detection fails. Without Node.js runtime, the release command fails and blocks deployment entirely. The implementer has no warning until they push to Railway and the build breaks.
- **Fix A ⭐ Recommended**: Add buildpack verification step to Phase 1 + railway.json
  - Strength: Explicit configuration prevents auto-detection failures. Railway reads railway.json for buildpack overrides. Adding Phase 1 step "Verify Railway buildpack" with `railway run npm --version` catches the issue before implementation starts.
  - Tradeoff: Requires railway CLI locally + active Railway project.
  - Confidence: HIGH — railway.json is Railway's official config file; npm presence check is a standard validation pattern.
  - Blind spot: If Railway project doesn't exist yet (fresh repo), this check will fail — implementer needs Railway setup first.
- **Fix B**: Add Phase 0.5 "Railway Buildpack Configuration" before Phase 1
  - Strength: Comprehensive — documents buildpack detection, explains how package.json triggers Node.js, includes verification.
  - Tradeoff: Adds a full phase for what's essentially a deployment prerequisite — increases plan length and implementation time.
  - Confidence: MEDIUM — more thorough but potentially over-engineered for what might "just work" once package.json exists.
  - Blind spot: Same as Fix A — requires Railway project setup first.
- **Decision**: FIXED via Fix A — Added Railway buildpack configuration section to Phase 1 with railway.json creation and verification step. Phase 1 now includes `railway run npm --version` as automated verification.

### F2 — Progress↔Phase mismatch in Phase 2

- **Severity**: ⚠️ WARNING
- **Impact**: 🏃 LOW — quick decision; fix is obvious and narrowly scoped
- **Dimension**: Plan Completeness
- **Location**: Phase 2 — Authentication URLs & Views / Progress Section
- **Detail**: Success criteria in Phase 2 (lines 225-236) include "URL routing works: `python manage.py show_urls`" but this is NOT in the Progress section. Progress at line 516 shows "2.1 No import errors: python manage.py check passes" which combines two distinct checks. The Progress section must have exactly one checkbox per Success Criteria item per the Progress format convention. /10x-implement will fail to parse mismatched criteria.
- **Fix**: Split 2.1 into two items and add URL routing check:
     - [ ] 2.1 URL routing works: `python manage.py show_urls` (or manual curl)
     - [ ] 2.2 No import errors: `python manage.py check` passes
     - [ ] 2.3 Migrations up to date: `python manage.py migrate` reports no pending
     (This matches the 3 criteria in "Automated Verification" at lines 226-229.)
- **Decision**: FIXED — Progress section now has 2.1-2.3 matching Phase 2 automated verification criteria exactly.

### F3 — username-as-email validation not in Phase 2 contract

- **Severity**: ⚠️ WARNING
- **Impact**: 🔎 MEDIUM — real tradeoff; pause to reason through it
- **Dimension**: Plan Completeness
- **Location**: Phase 2 — Signup View
- **Detail**: Plan-brief line 73 acknowledges: "Risk: If user enters non-email string as username, login still works but violates user expectation. Mitigation: Phase 2 signup view can add EmailField validation before saving." However, the Phase 2 signup view contract (lines 203-207) doesn't specify this EmailField validation. It just says "uses UserCreationForm" and "labels username field as 'Email'". An implementer following the contract literally will skip email validation, leaving the acknowledged risk unmitigated.
- **Fix A ⭐ Recommended**: Add EmailField validation to Phase 2 signup view contract
  - Strength: Closes the acknowledged gap. Contract becomes: "After form.is_valid(), validate username is valid email format using Django's EmailField validator. If invalid, add form error and re-render."
  - Tradeoff: Adds ~5 lines of code to signup view (import validators, try/except ValidationError, form.add_error).
  - Confidence: HIGH — this is the mitigation the plan-brief already named.
  - Blind spot: Browser HTML5 email input validation may catch this first, making server-side check redundant for most cases.
- **Fix B**: Accept the risk and document it as "post-MVP hardening"
  - Strength: Faster implementation — let browser validation handle it.
  - Tradeoff: Tech-savvy users or API clients can bypass HTML5 validation and create accounts with non-email usernames (e.g., "alice"). This breaks FR-001 expectation ("sign up with email").
  - Confidence: MEDIUM — depends on whether "email signup" is a hard PRD requirement or just UI sugar.
  - Blind spot: PRD interpretation — does FR-001 mandate email-format validation, or just "user provides email address"?
- **Decision**: FIXED via Fix A — Added EmailValidator to signup view contract with explicit validation logic and required imports.

## Summary

All findings have been addressed through targeted plan edits:

1. **Railway buildpack verification** added to Phase 1 to catch deployment issues early
2. **Progress section** now matches Phase 2 success criteria exactly
3. **Email validation** added to signup view contract to enforce FR-001 requirement

The plan is now **SOUND** and ready for implementation via `/10x-implement`.
