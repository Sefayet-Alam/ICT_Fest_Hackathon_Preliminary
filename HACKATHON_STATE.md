# HACKATHON_STATE — CoWork Booking API

**Current status:** Inspection + planning complete. Bug inventory built (24 confirmed). Visible test matrix written. **No source fixes applied yet** — awaiting approval to start execution. Baseline run pending.

## Challenge
- Type: **Bug-fix / codebase-repair** (black-box graded). Fixes must preserve the API contract exactly.
- Spec source of truth: `README.md` (16 business rules + API contract). PDF problem statement = same challenge (title page confirms "CoWork: Multi-Tenant Coworking Space Booking API"); PDF body not text-extractable (CID-subset fonts, no poppler/pypdf available) — README treated as authoritative.

## Stack
- Python 3.11, FastAPI 0.111.0, SQLAlchemy 2.0.30, Pydantic 2.7.1, PyJWT 2.8.0, SQLite (single file), uvicorn.
- JWT HS256, `JWT_SECRET` from env (dev default in `config.py`). One container, port 8000.

## Run commands
- Docker (graded path): `docker compose up --build` → http://localhost:8000
- Local:
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload   # serve
  ```

## Test commands
- Existing: `pytest` (single happy-path smoke test in `tests/test_smoke.py`).
- Visible matrix: `TESTCASES.md` (curl) + `TESTCASES.json` (54 machine-readable cases). Runner script TBD in execution phase.

## Docker status
- `Dockerfile`, `docker-compose.yml`, `.dockerignore` present. **Not yet verified to build** (Docker not run yet). Verify in Phase 6.

## Assumptions (non-blocker)
- README is authoritative; PDF restates it.
- SQLite default is intended (no external DB).
- Dev `JWT_SECRET` default acceptable; grader supplies its own env.
- Concurrency requirements (Rules 3,4,5,6,7,16) are actively graded — deliberate `time.sleep()` hooks in the code widen race windows to make these observable.

## Progress checklist
- [x] Read README / spec
- [x] Read all source files (`app/**`)
- [x] Read requirements, Dockerfile presence, .gitignore, config, smoke test
- [x] Confirm no committed secrets (see SECURITY_CHECK.md)
- [x] Build BUG_LEDGER.md (24 bugs)
- [x] Build TESTCASES.md + TESTCASES.json
- [ ] Baseline: pip install + pytest + smoke run (record output here)
- [ ] Fix bugs one-by-one (minimal diffs) + update bug_report.md
- [ ] Concurrency fixes (locks/atomicity) + deadlock fix
- [ ] Verify Docker build
- [ ] Security re-check before public push
- [ ] Final readiness / submission summary

## Unresolved issues / open questions
- Confirm intended semantics of `/admin/export` `include_all` (all-org vs own bookings). Current safe read: `include_all=true` = all users in org; `false` = caller's own. Fix will keep this but enforce org scope + 404 on cross-org room.
- Concurrency fix strategy: process-level `threading.Lock` around booking conflict/quota/reference critical sections is the pragmatic SQLite-compatible approach.

## Next actions
1. Run baseline (`pip install -r requirements.txt`, `pytest`) and record results here.
2. On approval, begin fixes in the order listed at the bottom of BUG_LEDGER.md (low-risk → high-value first).

## Latest git status summary
- Repo: cloned from `github.com/Sefayet-Alam/ICT_Fest_Hackathon_Preliminary` (upstream `AlchemistReturns/...`).
- HEAD: initial commit + docs commits. Working tree adds: BUG_LEDGER.md, TESTCASES.md, TESTCASES.json, HACKATHON_STATE.md, bug_report.md, HANDOFF_FOR_CODEX.md, SECURITY_CHECK.md.
- No source (`app/**`) changes yet.
