# HACKATHON_STATE — CoWork Booking API

**Current status:** All 24 planted bugs fixed and verified, plus 2 found in a
second-pass bug-hunt (H1: malformed datetime → 500, now 400; H2: concurrent
registration race → 500, now serialized). Full suite green (**64 passed**). Live
server smoke passes. `CLAUDE.md` added. Ready for final review / submission.
Docker build not run here (daemon down) — verify before submit.

## Challenge
- Type: **Bug-fix / codebase-repair**, black-box graded. Fixes preserve the API contract exactly.
- Spec source of truth: `README.md` (= PDF business rules 1–16 + API contract; user supplied the PDF text and it matches the README verbatim).

## Stack
- Python 3.11, FastAPI 0.111, SQLAlchemy 2.0, Pydantic 2.7, PyJWT 2.8, SQLite, uvicorn. JWT HS256. Port 8000.
- NOTE: pydantic 2.7.1 has no wheel for Python 3.13 — use **Python 3.11** locally (matches the Dockerfile).

## Run commands
- Docker (graded path): `docker compose up --build` → http://localhost:8000
- Local:
  ```bash
  python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --port 8000
  ```

## Test commands
```bash
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q                      # 64 passed
```
- `tests/test_smoke.py` — original happy-path (kept).
- `tests/test_spec.py` — 54 deterministic spec/reproduction cases (rules 1,2,3,4,6,8,9,10,11,12,13,14,15).
- `tests/test_concurrency.py` — 6 concurrency cases (rules 3,4,5,7,14,16); verified they fail without the fixes.
- Visible/editable matrix: `TESTCASES.md` + `TESTCASES.json` (94 cases, full rule+endpoint coverage).

## Baseline (pre-fix) vs now
- Original smoke: passed before and after.
- Spec suite pre-fix: **20 failures** (each a planted bug). Post-fix: **0 failures**.
- Concurrency suite: rate-limit test verified to FAIL when the lock is removed, PASS with it.

## Docker status
- `Dockerfile` (python:3.11-slim), `docker-compose.yml`, `.dockerignore` present and sound.
- **Not built here** (Docker daemon down). Verify:
  ```bash
  docker compose up --build      # then hit http://localhost:8000/health
  ```

## Assumptions
- README/PDF are authoritative and identical.
- SQLite default intended; `JWT_SECRET` from env (dev default fine; grader supplies its own).
- Concurrency rules (3,4,5,6,7,16) actively graded — deliberate `time.sleep()` race-wideners were in the code; fixes use `threading.Lock` (SQLite is single-writer) and were confirmed with a threaded client.

## Progress checklist
- [x] Inspect repo + spec; build BUG_LEDGER (24 bugs)
- [x] Visible tests first (TESTCASES.md/.json, 94 cases)
- [x] Baseline run recorded (smoke pass; 20 spec failures reproduced)
- [x] Fix all 24 bugs, minimal diffs, one cluster at a time
- [x] Reproduction + regression tests (test_spec.py, test_concurrency.py) — 61 passed
- [x] Live uvicorn smoke (health, JWT 900s, tz→UTC, booking)
- [x] bug_report.md complete
- [ ] `docker compose up --build` verified (needs daemon)
- [ ] Final security re-check + submission (see SECURITY_CHECK.md)
- [ ] draw.io diagrams (optional, after stability)

## Unresolved / known limitations
- Docker build unverified locally (daemon down) — low risk (base image = local env).
- Reference-code counter is in-memory (starts at 1000). Under a process restart that reuses a **persisted** DB volume, codes could repeat. Not an issue for a fresh grader container; a DB-seeded counter would remove even that edge case. No DB unique constraint was added to avoid restart-collision 500s.
- The `app/services/stats.py` module is now unused (stats derive from the DB); left in place to keep the diff minimal.

## Next actions
1. `docker compose up --build` once the daemon is available; hit `/health`.
2. Run `/security` review; confirm repo public-safe (note: problem-statement PDF is committed at `docs/` — decide whether that should be public).
3. Commit remaining changes and push.

## Latest git status summary
- Source changed: `app/timeutils.py`, `app/auth.py`, `app/routers/{auth,bookings,rooms}.py`, `app/services/{export,notifications,ratelimit,reference,refunds}.py` (10 files).
- Tests added: `tests/test_spec.py`, `tests/test_concurrency.py`.
- Docs updated: BUG_LEDGER, bug_report, HACKATHON_STATE, HANDOFF_FOR_CODEX, SECURITY_CHECK.
- `.venv/` and `cowork.db` correctly gitignored.

---

## Final Review — READY (with one unverified item)

Reviewed by: final-reviewer (independent, read-only pass). Date: 2026-07-09.

### Rubric scores (1-5)
- **Rules compliance:** 5/5 — Repo confirmed public (`https://github.com/Sefayet-Alam/ICT_Fest_Hackathon_Preliminary`, HTTP 200, raw README fetches). All commits timestamped 2026-07-09 (same day), no sign of pre-event code. README has setup, run, and test instructions and a clear tech-stack list (Python 3.11 / FastAPI / SQLAlchemy / SQLite / PyJWT / uvicorn — all standard OSS, named). No secrets committed; `.venv/` and `cowork.db` correctly gitignored and untracked.
- **Does it run?:** 4/5 — `requirements.txt` fully pinned (`fastapi==0.111.0`, `uvicorn[standard]==0.30.1`, `SQLAlchemy==2.0.30`, `pydantic==2.7.1`, `PyJWT==2.8.0`). No hardcoded local paths anywhere in `app/`, tests, README, or Docker files (grepped, zero hits). `Dockerfile`/`docker-compose.yml` are sound by inspection (correct COPY order, `EXPOSE 8000`, correct `CMD`, env vars supplied inline in compose — no missing `.env`). **Docker daemon was unavailable in this sandbox on two attempts, so `docker compose up --build` was never actually executed** — this is the single unverified claim in the whole submission. Local venv run and `pytest` were independently verified and work.
- **Working demo:** 5/5 — `pytest -q` independently re-run twice (once against the pre-existing DB, once after `rm -f cowork.db` for a clean slate): **64 passed, 0 failed** both times, ~31s. Test files: `tests/test_smoke.py` (1), `tests/test_spec.py` (55), `tests/test_concurrency.py` (8) = 64, matching the actual pytest count exactly (the "61 passed" figure in `CLAUDE.md`/`bug_report.md`/`HANDOFF_FOR_CODEX.md` is stale, pre-dating the H1/H2 second-pass tests — cosmetic only, not a functional issue).
- **Correctness:** 5/5 — Cross-checked `BUG_LEDGER.md`'s 24+2 entries against current source for every rule called out in the review brief: multi-tenancy 404s (rooms/availability/stats/bookings/export all scope by `org_id` via `_get_org_room`/join filters, cross-org confirmed 404 in tests), refund rounding (`(price_cents*percent+50)//100`, half-up, single source of truth echoed from the `RefundLog` row — response and stored value cannot diverge), JWT claims/lifetimes (`sub` string, `org`, `role`, `jti`, `iat`, `exp`, `type`; access `exp-iat`=900s exactly, refresh=7d), pagination (`.offset((page-1)*limit).limit(limit)`, ascending `start_time`+`id` tiebreak), cache invalidation symmetry (create invalidates availability+report; cancel invalidates report+availability — symmetric), and concurrency locks (`_booking_lock` around conflict+quota+insert and around cancel; `_register_lock` around register check-then-insert; independent locks for reference counter, rate limiter, notifications with consistent lock order to avoid deadlock). No remaining contract violation found in the read source. All BUG_LEDGER entries show `FIXED ✓ verified` and match code.
- **Security/publish-safety:** 4/5 — No BLOCK items. `SECURITY_CHECK.md`'s only open item is a **decision, not a defect**: `docs/ICT_Fest_Hackathon_Preliminary.pdf` (problem statement) is committed and will be public — organizers' call, not a leak. Passwords are PBKDF2-HMAC-SHA256 with per-user salt; `JWT_SECRET` has a clearly-labeled non-secret dev default. No `.env`/DB/credentials tracked (verified via `git ls-files`). Checklist itself has two unchecked boxes (`.env.example` optional, PDF decision) — should be explicitly closed out before push, not because either is unsafe, but because the doc claims "pending."
- **Tests:** 5/5 — `TESTCASES.json` has exactly 94 cases (`cases` array, machine-verified) with a `coverage` map. Automated suite is not a rubber stamp: concurrency tests assert strict invariants (e.g., `len(successes) == 1` for the double-booking race, `roles.count("admin") == 1` for concurrent registration), not loosened to "at least one passes." Spot-checked test_spec.py's cross-org tests — they hit `/rooms/{id}/availability` and `/bookings/{id}` for the multi-tenancy rule, which share the same guard helpers used by stats/export, so coverage is representative even though stats/export don't each get a dedicated cross-org test.
- **Polish:** 4/5 — No `print`/`TODO`/`FIXME`/debugger leftovers anywhere in `app/` (grepped, zero hits). README is clear and complete. Minor: stale "61 passed" references in three docs (cosmetic); `app/services/stats.py` is dead code left in place (acknowledged in the repo's own docs as intentional to minimize diff — acceptable); `BUG_LEDGER.md`'s REF1 "Fix plan" column says "add `unique=True` on column" but the actual shipped fix (confirmed in `models.py:55`) deliberately omits the DB constraint, relying on the lock instead — `bug_report.md` explains this reasoning correctly, so it's a **ledger/fix-plan wording mismatch**, not an actual bug (functionally satisfies rule 7 under concurrency per the passing `test_reference_codes_unique_under_concurrency`).

### Blockers (must fix to submit)
- [ ] **Actually run `docker compose up --build` and hit `GET /health`** before submitting — this was never executed successfully in this sandbox (Docker daemon down on every attempt) or, per `HACKATHON_STATE.md`'s own admission, during development either. This is the graded path; static inspection looks correct but has not been empirically confirmed end-to-end even once.

### Should-fix (loses points / cleanliness)
- [ ] Update the stale "61 passed" mentions in `CLAUDE.md`, `bug_report.md`, and `HANDOFF_FOR_CODEX.md` to "64 passed" (H1/H2 second-pass tests added 3 cases after those docs were first written).
- [ ] Resolve the two open `SECURITY_CHECK.md` checklist boxes explicitly (keep-or-remove the committed PDF; decide on `.env.example`) so the doc doesn't read as still-pending at submission time.
- [ ] Either fix `BUG_LEDGER.md`'s REF1 "Fix plan" cell to match the actual shipped fix (lock-only, no DB `unique=True`, as explained correctly in `bug_report.md`) or add the constraint — currently the two docs disagree with each other on what was done.

### Verified working (independently, this session)
- `pytest -q` → **64 passed, 0 failed**, reproduced twice (dirty and clean DB).
- Test-file count matches pytest count exactly (1 + 55 + 8 = 64).
- `TESTCASES.json` parses cleanly, 94 cases.
- Repo is genuinely public and fetchable (`curl` → HTTP 200, raw README fetch succeeds).
- All commits dated 2026-07-09 — no pre-event code smell.
- No secrets, `.env`, or DB files tracked in git; `.gitignore`/`.dockerignore` correct.
- No hardcoded local filesystem paths anywhere in source, tests, or Docker config.
- No debug/print/TODO leftovers in `app/`.
- Source-level re-verification of multi-tenancy scoping, refund rounding/consistency, JWT claim shape and lifetimes, pagination math, cache-invalidation symmetry, and all concurrency locks — all match `README.md`'s 16 rules as read.
