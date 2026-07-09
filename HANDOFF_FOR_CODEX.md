# HANDOFF_FOR_CODEX — CoWork Booking API

Continue without prior chat context. Read `bug_report.md`, `BUG_LEDGER.md`,
`TESTCASES.md`/`.json`, `HACKATHON_STATE.md`, and `README.md` (spec) first.

## Status: DONE (pending Docker build verification)
All 24 planted bugs are fixed and verified. `pytest` → **61 passed**. Live uvicorn
smoke passes. The only open items are a Docker build check and the final
security/submission review.

## What has been changed
Source (minimal, contract-preserving diffs):
- `app/timeutils.py` — offset→UTC conversion (T1).
- `app/routers/bookings.py` — strict overlap (B1); no past-start grace (B2); end>start + min-duration (B3); list asc/offset/limit (B5a-c); detail member-IDOR guard (B6) + removed start_time overwrite (B7); refund tiers via timedelta + 0% under 24h (B8a/b) + single half-up amount == RefundLog (B9); cancel invalidates availability (RM1) + create invalidates report (AD1); `_booking_lock` serializes create & cancel critical sections (B-CONC); removed artificial sleeps.
- `app/services/refunds.py` — half-up integer rounding, returns the entry (B9).
- `app/auth.py` — access lifetime 900s (A1); logout blacklist keyed by `jti` (A2); added `revoke_jti`/`is_revoked`.
- `app/routers/auth.py` — duplicate username → 409 (A4); refresh single-use rotation (A5).
- `app/services/export.py` — always org-scoped, cross-org room → 404 (EX1); removed unsafe `fetch_bookings_raw`.
- `app/routers/rooms.py` — stats derived live from DB (S1).
- `app/services/reference.py` — atomic counter under a lock (REF1).
- `app/services/ratelimit.py` — thread-safe bucket under a lock (RL1).
- `app/services/notifications.py` — consistent lock order, no deadlock (N1).

Tests added: `tests/test_spec.py` (54), `tests/test_concurrency.py` (6). Original `tests/test_smoke.py` unchanged and passing.

Docs: `BUG_LEDGER.md` (all FIXED ✓), `bug_report.md` (per-bug detail), `HACKATHON_STATE.md`, this file, `SECURITY_CHECK.md`.

## Remaining tasks
1. `docker compose up --build`; confirm `GET /health` → `{"status":"ok"}` (daemon was down during dev).
2. Final security review; decide whether `docs/ICT_Fest_Hackathon_Preliminary.pdf` (committed) should be in a public repo.
3. Optional: draw.io diagrams (architecture / request flow / security boundary).
4. Commit + push.

## Commands
```bash
python3.11 -m venv .venv && source .venv/bin/activate   # 3.11 required (pydantic 2.7.1 has no 3.13 wheel)
pip install -r requirements.txt pytest
pytest -q                        # expect: 61 passed
uvicorn app.main:app --port 8000 # manual/curl per TESTCASES.md
docker compose up --build        # graded container path
```

## Known limitations
- In-memory reference counter: could repeat codes only if the process restarts against a persisted DB volume (not a fresh grader run). Lock guarantees uniqueness under concurrent creation. A DB-seeded counter would close the edge case.
- `app/services/stats.py` is now unused (kept to minimize the diff).
- Docker build not executed locally.

## Next recommended action
Run the Docker build check, then the security review, then push. If any grader
assertion fails, reproduce it as a new case in `tests/test_spec.py` first, then
fix with the smallest change and re-run `pytest`.
