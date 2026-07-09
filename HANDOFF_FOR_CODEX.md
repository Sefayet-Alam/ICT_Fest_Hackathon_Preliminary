# HANDOFF_FOR_CODEX — CoWork Booking API

Continue without prior chat context. Read this + `BUG_LEDGER.md` + `TESTCASES.md`/`.json` + `README.md` (spec) first.

## Mission
Bug-fix challenge, black-box graded. Fix the confirmed bugs with **minimal diffs**, preserving the API contract exactly (paths, status codes, error `code` values, JSON field names, JWT claims). Do NOT add features, LLM/agents, frontends, or refactor unrelated code.

## What has been inspected
- Entire `app/**` source read against README's 16 business rules.
- Stack: FastAPI + SQLAlchemy + SQLite + PyJWT. Run: `docker compose up --build` (port 8000) or `uvicorn app.main:app`.
- Existing tests: only `tests/test_smoke.py` (one happy path). Visible matrix authored in `TESTCASES.*` (54 cases).
- Secrets: none committed (see SECURITY_CHECK.md).

## What has been changed
- **Docs only** so far: `BUG_LEDGER.md`, `TESTCASES.md`, `TESTCASES.json`, `HACKATHON_STATE.md`, `bug_report.md`, `SECURITY_CHECK.md`, this file.
- **No `app/**` source edits yet.**

## Remaining tasks (fix order — low-risk → high-value)
Each ID maps to a row in `BUG_LEDGER.md` and testcase(s) in `TESTCASES.*`.
1. **T1** `app/timeutils.py:12-13` — convert offset to UTC: `dt.astimezone(timezone.utc).replace(tzinfo=None)`.
2. **B1** `app/routers/bookings.py:50` — strict `<`: `if b.start_time < end and start < b.end_time`.
3. **B2** `bookings.py:86` — reject `start <= now` (drop the 300s grace).
4. **B3** `bookings.py:89-94` — reject `end <= start` and `duration_hours < 1`.
5. **B7** `bookings.py:166` — delete the line overwriting `start_time` with `created_at`.
6. **B6** `bookings.py:156-163` — add member-ownership check (mirror cancel's `:192-193`).
7. **B5a/b/c** `bookings.py:137-139` — `start_time.asc()`, `.offset((page-1)*limit)`, `.limit(limit)`.
8. **A4** `app/routers/auth.py:37-43` — raise `AppError(409,"USERNAME_TAKEN",...)` instead of returning 200.
9. **B8a/b** `bookings.py:200-206` — tiers: `notice >= timedelta(hours=48)` → 100; `>= timedelta(hours=24)` → 50; else **0**. Use timedelta, not floored hours.
10. **B9** `bookings.py:208` + `app/services/refunds.py` — single half-up value `(price_cents*percent + 50)//100`; have `log_refund` compute+store it and return the entry; router echoes `entry.amount_cents` so response == RefundLog.
11. **A1** `app/auth.py:50` — `timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)` (remove `* 60`) → exp−iat = 900.
12. **A2** `app/auth.py:97` — check `payload.get("jti") in _revoked_tokens` (not `sub`).
13. **A5** `app/routers/auth.py:81-93` + `app/auth.py` — blacklist the presented refresh `jti` on use; reject reuse with 401. (Add a refresh-jti set + check.)
14. **EX1** `app/services/export.py` — always org-scope; replace `fetch_bookings_raw` path with `_fetch_scoped(db, org_id, None, room_id)`; if `room_id` not in org → 404 `ROOM_NOT_FOUND`.
15. **RM1** `bookings.py` cancel — add `cache.invalidate_availability(booking.room_id, booking.start_time.date().isoformat())`.
16. **AD1** `bookings.py` create — add `cache.invalidate_report(user.org_id)`.
17. **S1** `app/routers/rooms.py:110` — compute stats live from DB (count + sum of confirmed bookings for the room) instead of `stats.get()`.
18. **REF1** `app/services/reference.py` — guard counter with `threading.Lock`; add `unique=True` on `Booking.reference_code` (`app/models.py:55`).
19. **RL1** `app/services/ratelimit.py` — guard bucket read-modify-write with `threading.Lock`.
20. **B-CONC** `bookings.py` — serialize conflict-check + insert (and quota) under a process `threading.Lock` (SQLite single-writer).
21. **N1** `app/services/notifications.py` — consistent lock order in both `notify_created` and `notify_cancelled` (email→audit in both), or collapse to one lock. Fixes deadlock (Rule 16).

## Commands to run
```bash
pip install -r requirements.txt
pytest                              # smoke
uvicorn app.main:app --port 8000    # manual/curl testing per TESTCASES.md
# concurrency cases (T-REF-UNIQUE, T-CONF-CONC, T-RATE-CONC, T-LIVENESS-DEADLOCK) need a
# parallel client (e.g. xargs -P / python threads / hey). Add scripts/ if helpful.
docker compose up --build           # verify graded container path (Phase 6)
```

## Known failures / not-yet-done
- Baseline not yet run/recorded.
- No source fixes applied.
- Concurrency tests require a parallel runner (not yet written).
- Docker build not yet verified.

## Next recommended action
Run baseline (`pytest`), then apply fixes 1→21 one at a time: reproduce with the mapped testcase, make the minimal edit, re-run that case + `pytest`, update `BUG_LEDGER.md` (→ FIXED/VERIFIED) and add the `bug_report.md` block, then commit with a `fix:`/`test:`/`docs:` message.
