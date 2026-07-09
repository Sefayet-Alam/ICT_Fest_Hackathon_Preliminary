# CoWork Booking API — Bug Report

24 planted bugs found and fixed, each reproduced by a visible failing test that
passes after the fix. Grading is black-box; every fix preserves the API contract
(paths, status codes, error codes, JSON field names, JWT claims).

- **Tests:** `pytest` → **61 passed** (54 spec + 6 concurrency + 1 original smoke).
- **Reproduction suites:** `tests/test_spec.py` (deterministic), `tests/test_concurrency.py` (rules 3/4/5/7/16).
- Line numbers below are pre-fix (against `Initial commit`).

## Summary

| ID | Rule | Title | Severity | Test(s) | Status |
|----|------|-------|----------|---------|--------|
| T1 | 1 | Offset datetime not converted to UTC | High | test_offset_input_converted_to_utc | FIXED |
| B2 | 2 | 300s past-start grace window | High | test_past_start_rejected_no_grace | FIXED |
| B3 | 2 | Zero/negative duration accepted | High | test_zero_duration_rejected, test_negative_duration_rejected | FIXED |
| B1 | 3 | Back-to-back bookings wrongly rejected | High | test_back_to_back_allowed | FIXED |
| B-CONC | 3,4 | Double-book / quota race | High | test_no_double_booking_under_concurrency, test_quota_under_concurrency | FIXED |
| RL1 | 5 | Rate limiter not thread-safe | Medium | test_rate_limit_under_concurrency | FIXED |
| B8a | 6 | 48h refund boundary excluded | Medium | test_refund_48h_boundary_is_100 | FIXED |
| B8b | 6 | <24h notice refunds 50% not 0% | High | test_refund_under_24h_is_zero | FIXED |
| B9 | 6 | Refund rounding + response≠RefundLog | High | test_refund_half_cent_rounds_up, test_refund_response_equals_refundlog | FIXED |
| REF1 | 7 | Reference-code duplicates under concurrency | High | test_reference_codes_unique_under_concurrency | FIXED |
| A1 | 8 | Access token lifetime 54000s not 900s | High | test_access_token_lifetime_900s | FIXED |
| A2 | 8 | Logout never invalidates token | Critical | test_logout_invalidates_token | FIXED |
| A5 | 8 | Refresh token reusable | Critical | test_refresh_single_use | FIXED |
| EX1 | 9 | Export cross-org data leak | Critical | test_export_cannot_leak_other_org | FIXED |
| B6 | 10 | Member IDOR reading others' bookings | Critical | test_member_cannot_read_others_booking | FIXED |
| B7 | contract | Detail overwrites start_time with created_at | High | test_detail_start_time_correct | FIXED |
| B5a | 11 | List order descending | Medium | test_list_ascending_by_start_time | FIXED |
| B5b | 11 | Pagination off-by-one page | High | test_list_page_one_returns_first_slice | FIXED |
| B5c | 11 | Limit param ignored (hardcoded 10) | High | test_list_limit_honored | FIXED |
| AD1 | 12 | Create doesn't invalidate report cache | High | test_report_reflects_new_booking | FIXED |
| RM1 | 13 | Cancel doesn't invalidate availability cache | High | test_availability_reflects_cancel | FIXED |
| S1 | 14 | Room stats drift from DB | Medium | test_stats_consistent_after_cancel, test_stats_consistent_under_concurrency | FIXED |
| A4 | 15 | Duplicate username returns 200 | High | test_register_duplicate_username_409 | FIXED |
| N1 | 16 | Notification lock-ordering deadlock | Critical | test_no_deadlock_on_concurrent_create_and_cancel | FIXED |

---

## T1 — Offset datetimes not converted to UTC (Rule 1)
- **Affected:** `app/timeutils.py` `parse_input_datetime`
- **Wrong:** offset-aware input had its tzinfo dropped (`dt.replace(tzinfo=None)`), keeping the wall-clock time instead of the UTC instant.
- **Why:** `12:00+06:00` was stored as `12:00` instead of `06:00Z`, corrupting all comparisons (conflict, quota, reports).
- **Repro:** book `2027-03-01T12:00:00+06:00`; expect stored/echoed `06:00:00`.
- **Fix:** `dt.astimezone(timezone.utc).replace(tzinfo=None)`.
- **Proof:** `test_offset_input_converted_to_utc`, `test_naive_input_treated_as_utc`.

## B1 — Back-to-back bookings wrongly rejected (Rule 3)
- **Affected:** `app/routers/bookings.py` `_has_conflict`
- **Wrong:** overlap used `<=` (`b.start_time <= end and start <= b.end_time`), so a booking ending exactly when another starts was flagged as a conflict.
- **Fix:** strict `<` on both comparisons (overlap iff `existing.start < new.end AND new.start < existing.end`).
- **Proof:** `test_back_to_back_allowed` (adjacent → 201), `test_overlap_conflict` (real overlap → 409).

## B2 — Past-start grace window (Rule 2)
- **Affected:** `create_booking`
- **Wrong:** `if start <= now - timedelta(seconds=300)` allowed starts up to 5 minutes in the past.
- **Fix:** `if start <= now`.
- **Proof:** `test_past_start_rejected_no_grace`.

## B3 — Zero/negative duration accepted (Rule 2)
- **Affected:** `create_booking`
- **Wrong:** only whole-hours and `>8h` were checked; `end == start` (0h) and `end < start` (negative) passed → 201 with price 0/negative.
- **Fix:** reject `end <= start`, and `duration_hours < MIN_DURATION_HOURS (1)`.
- **Proof:** `test_zero_duration_rejected`, `test_negative_duration_rejected`, `test_duration_min_and_max_ok`.

## B5a/B5b/B5c — Pagination & ordering (Rule 11)
- **Affected:** `list_bookings`
- **Wrong:** `order_by(start_time.desc())` (should be asc); `.offset(page*limit)` (page 1 skipped the first page); `.limit(10)` hardcoded (ignored `limit`).
- **Fix:** `start_time.asc()`, `.offset((page-1)*limit)`, `.limit(limit)`.
- **Proof:** `test_list_ascending_by_start_time`, `test_list_page_one_returns_first_slice`, `test_list_limit_honored`, `test_list_total_is_full_count`.

## B6 — Member IDOR on booking detail (Rule 10)
- **Affected:** `get_booking`
- **Wrong:** filtered by org only, so any member could read any booking in the org.
- **Fix:** added `if user.role != "admin" and booking.user_id != user.id: 404` (mirrors cancel).
- **Proof:** `test_member_cannot_read_others_booking`, `test_admin_can_read_any_org_booking`.

## B7 — Detail overwrote start_time with created_at (contract)
- **Affected:** `get_booking`
- **Wrong:** `response["start_time"] = iso_utc(booking.created_at)` clobbered the real start time.
- **Fix:** removed the line; `serialize_booking` already emits the correct `start_time`.
- **Proof:** `test_detail_start_time_correct`.

## B8a/B8b/B9 — Refund policy (Rule 6)
- **Affected:** `cancel_booking`, `app/services/refunds.py` `log_refund`
- **Wrong:** tier used floored-hours `> 48` (48h excluded from 100%); the `<24h` branch returned 50% instead of 0%; the amount was computed twice — router `round()` (banker's) and `log_refund` `int()` (truncation) — so it under-rounded and could differ from the stored RefundLog.
- **Fix:** compare with `timedelta` (`>=48h → 100`, `>=24h → 50`, else `0`); compute the amount once, half-up, with integer math `(price_cents*percent + 50)//100` inside `log_refund`, and return exactly `refund.amount_cents` so response == RefundLog.
- **Proof:** `test_refund_48h_boundary_is_100`, `test_refund_under_24h_is_zero`, `test_refund_half_cent_rounds_up` (501), `test_refund_response_equals_refundlog`, plus 100%/50% tiers and `test_single_refundlog_per_cancel`.

## A1 — Access token lifetime (Rule 8)
- **Affected:** `app/auth.py` `create_access_token`
- **Wrong:** `timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 60)` → 15×60 min = 54000s.
- **Fix:** `timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)` → exp − iat = 900.
- **Proof:** `test_access_token_lifetime_900s`, `test_jwt_required_claims`.

## A2 — Logout was a no-op (Rule 8)
- **Affected:** `app/auth.py` `get_token_payload`
- **Wrong:** logout stored the token `jti` in the blacklist, but the guard checked `payload.get("sub")` — which never matches a `jti`, so revoked tokens kept working.
- **Fix:** check `payload.get("jti") in _revoked_tokens`.
- **Proof:** `test_logout_invalidates_token`.

## A4 — Duplicate username returned 200 (Rule 15)
- **Affected:** `app/routers/auth.py` `register`
- **Wrong:** on an existing username it returned 200 with the existing user.
- **Fix:** raise `AppError(409, "USERNAME_TAKEN", …)`.
- **Proof:** `test_register_duplicate_username_409`, `test_register_admin_then_member_roles`.

## A5 — Refresh token reusable (Rule 8)
- **Affected:** `app/routers/auth.py` `refresh`, `app/auth.py`
- **Wrong:** refresh issued new tokens but never invalidated the presented one → infinite reuse.
- **Fix:** added shared `revoke_jti`/`is_revoked`; refresh rejects an already-used `jti` (401) and consumes the presented `jti` on success (single-use rotation).
- **Proof:** `test_refresh_single_use`, `test_refresh_rotates`.

## EX1 — Export cross-org data leak (Rule 9)
- **Affected:** `app/services/export.py` `generate_export`
- **Wrong:** `include_all=true` + `room_id` called `fetch_bookings_raw(room_id)` with no org filter → an admin could export another org's bookings.
- **Fix:** removed the unsafe helper; always route through the org-scoped query; validate the room belongs to the caller's org (else 404 `ROOM_NOT_FOUND`).
- **Proof:** `test_export_cannot_leak_other_org`, `test_export_header_exact`, `test_export_admin_only`.

## RM1 / AD1 — Stale caches (Rules 13 / 12)
- **Affected:** `create_booking`, `cancel_booking`
- **Wrong:** create invalidated only availability; cancel invalidated only the report — so cancels left stale availability and creates left stale usage reports.
- **Fix:** create now also invalidates the report cache; cancel now also invalidates the availability cache.
- **Proof:** `test_availability_reflects_cancel`, `test_report_reflects_new_booking`.

## S1 — Room stats drifted from the DB (Rule 14)
- **Affected:** `app/routers/rooms.py` `room_stats`
- **Wrong:** served in-memory counters (racy read-modify-write, lost on restart) that could diverge from the bookings.
- **Fix:** derive live from the DB (`COUNT` + `COALESCE(SUM(price_cents),0)` over confirmed bookings). Removed the now-unused `stats` side-effects from the booking paths.
- **Proof:** `test_stats_consistent_after_cancel`, `test_stats_consistent_under_concurrency`.

## REF1 — Reference-code duplicates under concurrency (Rule 7)
- **Affected:** `app/services/reference.py`
- **Wrong:** unguarded read-modify-write on a shared counter (with an artificial sleep) let concurrent creates share a code.
- **Fix:** guarded the increment with a `threading.Lock`; removed the race-widening sleep. (The booking critical section also serializes issuance.) A DB `unique` constraint was deliberately **not** added, to avoid turning a process-restart counter reset into 500s; the lock satisfies "unique under concurrent creation".
- **Proof:** `test_reference_codes_unique_under_concurrency`.

## RL1 — Rate limiter not thread-safe (Rule 5)
- **Affected:** `app/services/ratelimit.py`
- **Wrong:** unguarded trim-append-count on the per-user bucket (with a sleep) lost updates under concurrency, letting >20/60s through.
- **Fix:** wrapped the critical section in a `threading.Lock`; removed the sleep. All requests still count (limit check after recording).
- **Proof:** `test_rate_limit_under_concurrency` (verified it fails without the lock).

## B-CONC — Double-book / quota race (Rules 3, 4)
- **Affected:** `create_booking`, `cancel_booking`
- **Wrong:** conflict/quota check and insert were not atomic; concurrent requests for the same slot both passed → double-booking / quota bypass. Concurrent cancels of the same booking could write two RefundLogs.
- **Fix:** a module-level `_booking_lock` serializes the create critical section (conflict + quota + reference + insert + commit) and the cancel critical section (re-read status under the lock → single refund). Removed the artificial `time.sleep()` race-wideners, improving liveness.
- **Proof:** `test_no_double_booking_under_concurrency`, `test_quota_under_concurrency`.

## N1 — Notification deadlock (Rule 16)
- **Affected:** `app/services/notifications.py`
- **Wrong:** `notify_created` acquired email→audit while `notify_cancelled` acquired audit→email; a concurrent create + cancel deadlocked and hung the service.
- **Fix:** consistent lock order (email→audit) in both.
- **Proof:** `test_no_deadlock_on_concurrent_create_and_cancel` (completes within a 30s timeout).
