# CoWork Booking API — Bug Report

Final tie-breaker documentation. One section per **confirmed & fixed** bug.
Status here is filled during the fix phase; entries below are staged from `BUG_LEDGER.md`
and marked **PENDING FIX** until the change + proof are in place.

> Format per bug: Title · Affected file(s):line · What was wrong · Why it broke behavior ·
> How to reproduce · How it was fixed · Tests proving the fix.

---

## Summary table (fill "Fixed" + commit as we go)

| ID | Rule | Title | Severity | Status | Commit |
|----|------|-------|----------|--------|--------|
| T1 | 1 | Offset datetimes not converted to UTC | High | PENDING FIX | |
| B1 | 3 | Back-to-back bookings wrongly rejected | High | PENDING FIX | |
| B2 | 2 | 300s past-start grace window | High | PENDING FIX | |
| B3 | 2 | Zero/negative duration accepted | High | PENDING FIX | |
| B7 | contract | Detail overwrites start_time with created_at | High | PENDING FIX | |
| B6 | 10 | Member IDOR reading others' bookings | Critical | PENDING FIX | |
| B5a | 11 | List order descending | Medium | PENDING FIX | |
| B5b | 11 | Pagination off-by-one page | High | PENDING FIX | |
| B5c | 11 | Limit param ignored (hardcoded 10) | High | PENDING FIX | |
| A4 | 15 | Duplicate username returns 200 | High | PENDING FIX | |
| B8a | 6 | Refund 48h boundary excludes 48h | Medium | PENDING FIX | |
| B8b | 6 | <24h notice refunds 50% not 0% | High | PENDING FIX | |
| B9 | 6 | Refund rounding + response≠RefundLog | High | PENDING FIX | |
| A1 | 8 | Access token lifetime 54000s not 900s | High | PENDING FIX | |
| A2 | 8 | Logout never invalidates token | Critical | PENDING FIX | |
| A5 | 8 | Refresh token reusable | Critical | PENDING FIX | |
| EX1 | 9 | Export cross-org data leak | Critical | PENDING FIX | |
| RM1 | 13 | Cancel doesn't invalidate availability cache | High | PENDING FIX | |
| AD1 | 12 | Create doesn't invalidate report cache | High | PENDING FIX | |
| S1 | 14 | Room stats drift from DB | Medium | PENDING FIX | |
| REF1 | 7 | Reference-code duplicates under concurrency | High | PENDING FIX | |
| RL1 | 5 | Rate limiter not thread-safe | Medium | PENDING FIX | |
| B-CONC | 3,4 | Double-book/quota race | High | PENDING FIX | |
| N1 | 16 | Notification lock-ordering deadlock | Critical | PENDING FIX | |

---

<!-- Populate one block per bug as it is fixed. Template: -->

<!--
## <ID> — <Title>
- **Affected:** `path:line`
- **What was wrong:** …
- **Why it caused incorrect behavior:** …
- **How to reproduce:** … (link testcase ID)
- **How it was fixed:** … (diff summary, minimal change)
- **Tests proving the fix:** <testcase IDs>; before: FAIL, after: PASS.
-->
