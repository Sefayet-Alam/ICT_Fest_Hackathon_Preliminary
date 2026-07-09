# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CoWork is a multi-tenant coworking-space booking REST API (FastAPI + SQLAlchemy + SQLite).
This repo is a **bug-fix challenge**: `README.md` is the authoritative behavioral spec
(16 numbered business rules + an exact API contract) and grading is **black-box** — a grader
builds the container and asserts behavior against those rules by talking to the API only.

**The contract is law.** When changing code, preserve paths, HTTP status codes, error `code`
strings, JSON field names, and JWT claims exactly as written in `README.md`. A "cleaner"
response shape is a failed test. Fix behavior with the smallest change; do not refactor
unrelated code.

## Commands

Use **Python 3.11** — `pydantic==2.7.1` has no wheel for 3.13 and won't build there. The
Dockerfile pins `python:3.11-slim`.

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest      # pytest is not in requirements.txt

pytest -q                                    # full suite (expect: 61 passed)
pytest tests/test_spec.py -q                 # deterministic spec/reproduction cases
pytest tests/test_concurrency.py -q          # rules 3,4,5,7,14,16 (threaded)
pytest tests/test_spec.py::test_back_to_back_allowed -q   # a single test

uvicorn app.main:app --port 8000             # run locally (schema auto-creates on startup)
docker compose up --build                    # graded container path -> http://localhost:8000
```

Delete the SQLite file between runs for a clean slate: `rm -f cowork.db`.

## Test layout

- `tests/test_smoke.py` — original happy-path (do not remove; it is the reference smoke test).
- `tests/test_spec.py` — one deterministic assertion per business rule/edge; asserts the
  **spec** behavior so a planted bug shows up as a failing test.
- `tests/test_concurrency.py` — fires requests via `ThreadPoolExecutor`; FastAPI runs sync
  endpoints in a threadpool, so these exercise real race windows (double-book, quota,
  rate-limit, reference-code uniqueness, notification deadlock). To confirm a concurrency
  test has teeth, temporarily remove the relevant lock and watch it fail.
- `TESTCASES.md` / `TESTCASES.json` — the human-visible, editable 94-case matrix (master =
  JSON, with a `coverage` map over all 16 rules and 15 endpoints). Keep both in sync.

## Architecture

Request flow: `app/main.py` wires routers and registers the `AppError` handler.
`app/routers/{auth,rooms,bookings,admin,health}.py` are thin HTTP layers; domain side-effects
live in `app/services/{refunds,reference,ratelimit,stats,notifications,export,cache}.py`.

- **Errors:** raise `AppError(status, code, detail)` (`app/errors.py`); the handler renders
  `{"detail", "code"}`. Every business-rule violation uses this, never `HTTPException`.
- **Auth:** `app/auth.py` issues/verifies JWTs (HS256, secret from `JWT_SECRET` env).
  `get_current_user`/`require_admin` are FastAPI dependencies. Revocation is a single
  in-memory `jti` set (`_revoked_tokens`) shared by logout (access) and refresh single-use.
- **Datetime convention (Rule 1):** everything is stored **naive-UTC**. `parse_input_datetime`
  converts offset-aware input to UTC then strips tzinfo; naive input is treated as UTC.
  `iso_utc` renders stored datetimes back with a UTC designator. All comparisons assume
  naive-UTC — never mix aware/naive.
- **Multi-tenancy (Rule 9):** every read/write is scoped by the caller's `org_id`, and a
  cross-org id must behave as non-existent (`404`). Bookings/rooms are reached via a join on
  `Room.org_id == user.org_id`; check this on every new code path.
- **Concurrency:** SQLite is single-writer and sync endpoints run in a threadpool, so shared
  mutable state is guarded by `threading.Lock`. The booking conflict/quota check + insert and
  the cancel status-check + refund run under a module-level `_booking_lock` in
  `bookings.py`; the reference counter and rate-limiter each guard their own critical section.
  Rules 3/4/5/6/7/16 are graded "under concurrent requests" — preserve these locks.
- **Caches:** `cache.py` holds in-memory usage-report and availability caches. They must be
  invalidated **symmetrically** — booking create and cancel each invalidate *both* the
  room's availability (by date) and the org's report — or reads go stale (Rules 12/13).
- **Live-derived stats:** room stats (Rule 14) are computed directly from the bookings table,
  not from a counter, so they stay consistent under concurrency. `app/services/stats.py` is
  now unused legacy.

## Working the challenge

Test-first: reproduce a suspected bug as a failing case in `tests/test_spec.py` (or
`test_concurrency.py`), make the minimal fix, re-run that test then the full suite, and update
`BUG_LEDGER.md` (status), `bug_report.md` (root cause + proof), and `HACKATHON_STATE.md`.
`HANDOFF_FOR_CODEX.md` is the cross-agent continuation note. Boundary/refund-tier tests are
timing-sensitive — derive both bookings from one shared base time and use minute-level buffers
rather than separate `now()` calls.
