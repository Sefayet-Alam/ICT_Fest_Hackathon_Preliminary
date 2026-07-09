# TESTCASES — CoWork Booking API (visible & editable)

**`TESTCASES.json` is the master** (94 cases, machine-runnable). This file is the human view, generated to match it. Edit either; keep IDs in sync.

Base URL `http://localhost:8000`. Source of truth = problem-statement business rules (1–16) + API contract.

Placeholders (`$ADMIN`,`$ROOM`,`$BID`,`$OTHER_ORG_ROOM`,`<t>`,`<now+2h>`, …) are filled by the runner.

## Coverage

- **Total:** 94 cases · **Critical:** 46 · Rules missing: NONE · Endpoints missing: NONE

### By business rule

| Rule | Topic | Cases |
|---|---|---|
| 1 | Datetimes/UTC | T-TZ-OFFSET, T-TZ-NAIVE, T-TZ-RESPONSE-DESIGNATOR |
| 2 | Price & booking window | T-ROOM-CREATE, T-PRICE, T-WIN-MIN, T-WIN-MAX, T-WIN-9H, T-WIN-HALF, T-WIN-ZERO, T-WIN-NEG, T-WIN-PAST, T-WIN-FUTURE-OK, T-BOOK-422 |
| 3 | No double-booking | T-CONF-OVERLAP, T-CONF-BACK2BACK, T-CONF-CANCELLED-IGNORED, T-CONF-CONC |
| 4 | Booking quota | T-QUOTA, T-QUOTA-OUTSIDE, T-QUOTA-CANCELLED, T-QUOTA-CONC |
| 5 | Rate limit | T-RATE, T-RATE-CONC |
| 6 | Cancellation & refund | T-DETAIL-REFUNDS, T-REFUND-100, T-REFUND-48, T-REFUND-50, T-REFUND-24, T-REFUND-0, T-REFUND-ROUND, T-REFUND-CONSISTENT, T-CANCEL-ONE-REFUNDLOG, T-CANCEL-DUP, T-CANCEL-ADMIN, T-CANCEL-CONC, T-EXPORT-HEADER |
| 7 | Reference codes | T-REF-UNIQUE, T-REF-FORMAT |
| 8 | Auth/JWT | T-LOGIN-OK, T-LOGIN-BAD, T-LOGIN-UNKNOWN-ORG, T-AUTH-REFRESH-ROTATE, T-AUTH-REFRESH-REUSE, T-AUTH-REFRESH-WRONGTYPE, T-AUTH-LOGOUT, T-LOGOUT-NOAUTH, T-JWT-EXP, T-JWT-REFRESH-EXP, T-JWT-CLAIMS, T-AUTH-MISSING, T-AUTH-BADTOKEN, T-AUTH-EXPIRED, T-AUTH-REFRESH-AS-ACCESS |
| 9 | Multi-tenancy | T-ROOMS-LIST, T-ROOM-CREATE-FORBIDDEN, T-ROOMS-LIST-TENANT, T-TENANT-ROOM, T-TENANT-STATS, T-BOOK-ROOM-NOTFOUND, T-TENANT-BOOKING, T-TENANT-REPORT, T-EXPORT-CROSSORG, T-EXPORT-ADMIN-ONLY |
| 10 | Booking visibility | T-VIS-LIST-OWN, T-DETAIL-STARTTIME, T-VIS-IDOR-GET, T-VIS-ADMIN-GET, T-CANCEL-AUTH |
| 11 | Pagination & ordering | T-LIST-ORDER, T-LIST-TIES, T-LIST-PAGE1, T-LIST-PAGE2, T-LIST-LIMIT, T-LIST-LIMIT-MAX, T-LIST-TOTAL |
| 12 | Usage report | T-REPORT, T-REPORT-ZERO-ROOMS, T-REPORT-EXCL-CANCEL, T-REPORT-RANGE, T-REPORT-STALE, T-REPORT-ADMIN-ONLY |
| 13 | Availability | T-AVAIL, T-AVAIL-CREATE-IMMEDIATE, T-AVAIL-STALE, T-AVAIL-DATE-FILTER |
| 14 | Room stats | T-STATS-DERIVED, T-STATS-CONC |
| 15 | Registration | T-REG-ADMIN, T-REG-MEMBER, T-REG-DUP, T-REG-422 |
| 16 | Liveness | T-HEALTH, T-LIVENESS-DEADLOCK |

### By endpoint

| Endpoint | Cases |
|---|---|
| `POST /auth/register` | T-REG-ADMIN, T-REG-MEMBER, T-REG-DUP, T-REG-422 |
| `POST /auth/login` | T-LOGIN-OK, T-LOGIN-BAD, T-LOGIN-UNKNOWN-ORG, T-JWT-EXP, T-JWT-REFRESH-EXP, T-JWT-CLAIMS |
| `POST /auth/refresh` | T-AUTH-REFRESH-ROTATE, T-AUTH-REFRESH-REUSE, T-AUTH-REFRESH-WRONGTYPE |
| `POST /auth/logout` | T-AUTH-LOGOUT, T-LOGOUT-NOAUTH |
| `GET /rooms` | T-AUTH-MISSING, T-AUTH-BADTOKEN, T-AUTH-EXPIRED, T-AUTH-REFRESH-AS-ACCESS, T-ROOMS-LIST, T-ROOMS-LIST-TENANT |
| `POST /rooms` | T-ROOM-CREATE, T-ROOM-CREATE-FORBIDDEN |
| `GET /rooms/{id}/availability` | T-AVAIL, T-AVAIL-CREATE-IMMEDIATE, T-AVAIL-STALE, T-AVAIL-DATE-FILTER, T-TENANT-ROOM |
| `GET /rooms/{id}/stats` | T-STATS-DERIVED, T-STATS-CONC, T-TENANT-STATS |
| `POST /bookings` | T-PRICE, T-WIN-MIN, T-WIN-MAX, T-WIN-9H, T-WIN-HALF, T-WIN-ZERO, T-WIN-NEG, T-WIN-PAST, T-WIN-FUTURE-OK, T-TZ-OFFSET, T-TZ-NAIVE, T-TZ-RESPONSE-DESIGNATOR, T-CONF-OVERLAP, T-CONF-BACK2BACK, T-CONF-CANCELLED-IGNORED, T-CONF-CONC, T-QUOTA, T-QUOTA-OUTSIDE, T-QUOTA-CANCELLED, T-QUOTA-CONC, T-RATE, T-RATE-CONC, T-BOOK-ROOM-NOTFOUND, T-REF-UNIQUE, T-REF-FORMAT, T-BOOK-422, T-LIVENESS-DEADLOCK |
| `GET /bookings` | T-LIST-ORDER, T-LIST-TIES, T-LIST-PAGE1, T-LIST-PAGE2, T-LIST-LIMIT, T-LIST-LIMIT-MAX, T-LIST-TOTAL, T-VIS-LIST-OWN |
| `GET /bookings/{id}` | T-DETAIL-STARTTIME, T-DETAIL-REFUNDS, T-VIS-IDOR-GET, T-VIS-ADMIN-GET, T-TENANT-BOOKING |
| `POST /bookings/{id}/cancel` | T-REFUND-100, T-REFUND-48, T-REFUND-50, T-REFUND-24, T-REFUND-0, T-REFUND-ROUND, T-REFUND-CONSISTENT, T-CANCEL-ONE-REFUNDLOG, T-CANCEL-DUP, T-CANCEL-AUTH, T-CANCEL-ADMIN, T-CANCEL-CONC |
| `GET /admin/usage-report` | T-REPORT, T-REPORT-ZERO-ROOMS, T-REPORT-EXCL-CANCEL, T-REPORT-RANGE, T-REPORT-STALE, T-REPORT-ADMIN-ONLY, T-TENANT-REPORT |
| `GET /admin/export` | T-EXPORT-HEADER, T-EXPORT-CROSSORG, T-EXPORT-ADMIN-ONLY |
| `GET /health` | T-HEALTH |

## Auth setup (used by most cases)
```bash
curl -s localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"admin","password":"pw12345"}'
ADMIN=$(curl -s localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"admin","password":"pw12345"}' | jq -r .access_token)
curl -s localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"bob","password":"pw12345"}'
MEMBER=$(curl -s localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"bob","password":"pw12345"}' | jq -r .access_token)
ROOM=$(curl -s localhost:8000/rooms -H "Authorization: Bearer $ADMIN" -H 'Content-Type: application/json' \
  -X POST -d '{"name":"Focus","capacity":4,"hourly_rate_cents":1000}' | jq -r .id)
```

## Cases


### `POST /auth/register`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-REG-ADMIN |  | 15 | Register unknown org -> admin | POST | 201 user_id=int | First user in unknown org becomes admin — _fail: role != admin_ |  |
| T-REG-MEMBER |  | 15 | Register known org -> member | POST | 201 role=member | Known org join = member — _fail: role != member_ |  |
| T-REG-DUP | 🔴 | 15 | Duplicate username -> 409 USERNAME_TAKEN | POST | 409 code=USERNAME_TAKEN | Duplicate username within org rejected — _fail: 200 or 500_ | A4 |
| T-REG-422 |  | 15 | Missing field -> 422 framework validation | POST | 422 detail=list | Missing required field triggers FastAPI 422 — _fail: non-422_ |  |

### `POST /auth/login`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-LOGIN-OK |  | 8 | Login returns token pair | POST | 200 access_token=str | Valid creds return access+refresh+bearer — _fail: non-200 or missing token_ |  |
| T-LOGIN-BAD | 🔴 | 8 | Bad credentials -> 401 | POST | 401 code=INVALID_CREDENTIALS | Wrong password rejected — _fail: other status_ |  |
| T-LOGIN-UNKNOWN-ORG |  | 8 | Login unknown org -> 401 | POST | 401 code=INVALID_CREDENTIALS | Unknown org treated as invalid creds — _fail: 500 or other_ |  |
| T-JWT-EXP | 🔴 | 8 | Access token exp-iat == 900s | DECODE | — exp_minus_iat=900 | Access token lifetime is exactly 900 seconds — _fail: 54000 or other_ | A1 |
| T-JWT-REFRESH-EXP |  | 8 | Refresh token exp-iat == 604800s | DECODE | — exp_minus_iat=604800 | Refresh token lifetime is 7 days — _fail: wrong lifetime_ |  |
| T-JWT-CLAIMS | 🔴 | 8 | Access token carries required claims | DECODE | — sub=str | JWT includes sub(str),org,role,jti,iat,exp,type — _fail: missing/renamed claim_ |  |

### `POST /auth/refresh`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-AUTH-REFRESH-ROTATE |  | 8 | Refresh rotates tokens | POST | 200 access_token=str | Refresh returns a new access+refresh pair — _fail: non-200_ |  |
| T-AUTH-REFRESH-REUSE | 🔴 | 8 | Refresh token single-use | POST | 401 | Presented refresh token invalidated after one use — _fail: 200 (reusable)_ | A5 |
| T-AUTH-REFRESH-WRONGTYPE |  | 8 | Access token in refresh body -> 401 | POST | 401 | Non-refresh token rejected on refresh — _fail: 200_ |  |

### `POST /auth/logout`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-AUTH-LOGOUT | 🔴 | 8 | Logout invalidates presented access token | SEQUENCE | 401 | Reusing access token after logout -> 401 — _fail: 200 after logout_ | A2 |
| T-LOGOUT-NOAUTH |  | 8 | Logout without token -> 401 | POST | 401 | Logout requires a valid access token — _fail: other_ |  |

### `GET /rooms`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-AUTH-MISSING | 🔴 | 8 | No token on protected route -> 401 | GET | 401 | Missing Authorization header rejected — _fail: other_ |  |
| T-AUTH-BADTOKEN |  | 8 | Garbage token -> 401 | GET | 401 | Invalid/undecodable token rejected — _fail: 200/500_ |  |
| T-AUTH-EXPIRED |  | 8 | Blacklisted (logged-out) token -> 401 | GET | 401 | Revoked token rejected on later use — _fail: 200_ |  |
| T-AUTH-REFRESH-AS-ACCESS |  | 8 | Refresh token used as Bearer -> 401 | GET | 401 | type=refresh rejected on access-protected route — _fail: 200_ |  |
| T-ROOMS-LIST |  | 9 | List rooms in caller's org | GET | 200 [] | Returns rooms for caller's org ordered by id — _fail: wrong/foreign rooms_ |  |
| T-ROOMS-LIST-TENANT | 🔴 | 9 | Room list is org-scoped | GET | 200 only_own_org=True | Caller never sees another org's rooms — _fail: foreign-org rooms present_ |  |

### `POST /rooms`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-ROOM-CREATE |  | 2 | Admin creates room | POST | 201 id=int | Admin creates a room in own org — _fail: non-201/wrong shape_ |  |
| T-ROOM-CREATE-FORBIDDEN | 🔴 | 9 | Member cannot create room -> 403 | POST | 403 code=FORBIDDEN | Only admin may create rooms — _fail: 201_ |  |

### `GET /rooms/{id}/availability`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-AVAIL |  | 13 | Availability lists busy intervals sorted | GET | 200 room_id=int | Confirmed bookings on date returned as sorted busy intervals — _fail: missing/unsorted_ |  |
| T-AVAIL-CREATE-IMMEDIATE |  | 13 | New booking appears immediately | GET | 200 busy_includes_new=True | Availability reflects newly created booking at once — _fail: new booking missing (stale)_ |  |
| T-AVAIL-STALE | 🔴 | 13 | Cancel reflected in availability | GET | 200 busy_excludes_cancelled=True | Cancelled booking removed from busy immediately — _fail: still busy (stale cache)_ | RM1 |
| T-AVAIL-DATE-FILTER |  | 13 | Only bookings starting that UTC date | GET | 200 only_that_date=True | Bookings starting on other dates excluded — _fail: wrong-day intervals present_ |  |
| T-TENANT-ROOM | 🔴 | 9 | Cross-org room id -> 404 | GET | 404 code=ROOM_NOT_FOUND | Foreign-org room behaves as non-existent — _fail: 200/leak_ |  |

### `GET /rooms/{id}/stats`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-STATS-DERIVED | 🔴 | 14 | Stats equal DB-derived values | GET | 200 room_id=int | count/revenue always match confirmed bookings (create then cancel) — _fail: drift from DB_ | S1 |
| T-STATS-CONC | 🔴 | 14 | Stats consistent after concurrent bursts | CONCURRENT | 200 consistent_with_bookings=True | Stats reconcile with bookings after concurrency — _fail: counter drift/race_ |  |
| T-TENANT-STATS |  | 9 | Cross-org stats -> 404 | GET | 404 code=ROOM_NOT_FOUND | Foreign-org room stats non-existent — _fail: 200/leak_ |  |

### `POST /bookings`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-PRICE |  | 2 | Price = rate x whole hours | POST | 201 price_cents=2000 | 2h at 1000/hr = 2000 — _fail: wrong price_ |  |
| T-WIN-MIN |  | 2 | 1h duration allowed (min boundary) | POST | 201 price_cents=int | Duration 1h accepted — _fail: 400_ |  |
| T-WIN-MAX |  | 2 | 8h duration allowed (max boundary) | POST | 201 price_cents=int | Duration 8h accepted — _fail: 400_ |  |
| T-WIN-9H |  | 2 | 9h duration -> 400 | POST | 400 code=INVALID_BOOKING_WINDOW | Duration over 8h rejected — _fail: 201_ |  |
| T-WIN-HALF |  | 2 | Non-whole hours -> 400 | POST | 400 code=INVALID_BOOKING_WINDOW | 1.5h rejected (whole hours only) — _fail: 201_ |  |
| T-WIN-ZERO | 🔴 | 2 | end == start -> 400 | POST | 400 code=INVALID_BOOKING_WINDOW | Zero-length booking rejected — _fail: 201 price 0_ | B3 |
| T-WIN-NEG | 🔴 | 2 | end < start -> 400 | POST | 400 code=INVALID_BOOKING_WINDOW | end before start rejected — _fail: 201/negative price_ | B3 |
| T-WIN-PAST | 🔴 | 2 | Past start (no grace) -> 400 | POST | 400 code=INVALID_BOOKING_WINDOW | start_time strictly future; any past rejected — _fail: 201_ | B2 |
| T-WIN-FUTURE-OK |  | 2 | Near-future start accepted | POST | 201 | Start a few minutes ahead is valid — _fail: 400_ |  |
| T-TZ-OFFSET | 🔴 | 1 | Offset input converted to UTC | SEQUENCE | 201 stored_start_utc=2026-12-01T06:00:00+00:00 | 12:00+06:00 stored/echoed as 06:00Z — _fail: echoes 12:00 (offset dropped)_ | T1 |
| T-TZ-NAIVE |  | 1 | Naive input treated as UTC | SEQUENCE | 201 stored_start_utc=2026-12-01T12:00:00+00:00 | Naive 12:00 stored as 12:00Z — _fail: shifted by local tz_ |  |
| T-TZ-RESPONSE-DESIGNATOR |  | 1 | Response datetimes carry UTC designator | POST | 201 start_time_has_utc_designator=True | All response datetimes end with Z or +00:00 — _fail: naive/no designator_ |  |
| T-CONF-OVERLAP |  | 3 | Overlapping confirmed -> 409 | POST | 409 code=ROOM_CONFLICT | True overlap rejected — _fail: 201_ |  |
| T-CONF-BACK2BACK | 🔴 | 3 | Back-to-back allowed | POST | 201 | Adjacent bookings (end==start) allowed — _fail: 409_ | B1 |
| T-CONF-CANCELLED-IGNORED |  | 3 | Cancelled booking does not block | POST | 201 | Overlap with a cancelled booking is allowed — _fail: 409_ |  |
| T-CONF-CONC | 🔴 | 3 | No double-book under concurrency | CONCURRENT | — success_count=1 | Exactly one 201, others 409 under concurrency — _fail: >=2 success_ | B-CONC |
| T-QUOTA | 🔴 | 4 | 4th booking in window -> 409 | POST | 409 code=QUOTA_EXCEEDED | Max 3 confirmed in (now,+24h] — _fail: 201_ |  |
| T-QUOTA-OUTSIDE |  | 4 | Start beyond 24h not quota-limited | POST | 201 | Window is (now,+24h]; later start unaffected — _fail: 409_ |  |
| T-QUOTA-CANCELLED |  | 4 | Cancelled booking frees quota | POST | 201 | Only confirmed count toward quota — _fail: 409_ |  |
| T-QUOTA-CONC | 🔴 | 4 | Quota holds under concurrency | CONCURRENT | — confirmed_in_window_max=3 | Never exceeds 3 confirmed in window under concurrency — _fail: >3 confirmed_ | B-CONC |
| T-RATE | 🔴 | 5 | 21st request in 60s -> 429 | SEQUENCE | 429 code=RATE_LIMITED | 20/60s per user; all requests count; 21st rejected — _fail: all 201_ |  |
| T-RATE-CONC | 🔴 | 5 | Rate limit holds under concurrency | CONCURRENT | — passed_max=20 | At most 20 pass under concurrency — _fail: >20 pass_ | RL1 |
| T-BOOK-ROOM-NOTFOUND | 🔴 | 9 | Booking unknown/cross-org room -> 404 | POST | 404 code=ROOM_NOT_FOUND | Nonexistent or foreign-org room rejected — _fail: 201/500_ |  |
| T-REF-UNIQUE | 🔴 | 7 | Reference codes unique under concurrency | CONCURRENT | 201 reference_codes=all distinct | No duplicate reference_code even concurrently — _fail: duplicate codes_ | REF1 |
| T-REF-FORMAT |  | 7 | Reference code format CW-###### | POST | 201 reference_code=CW-\d{6} | reference_code matches CW-###### pattern — _fail: malformed code_ |  |
| T-BOOK-422 |  | 2 | Missing booking field -> 422 | POST | 422 detail=list | Missing room_id/time triggers 422 — _fail: non-422_ |  |
| T-LIVENESS-DEADLOCK | 🔴 | 16 | No hang on concurrent create+cancel | CONCURRENT | — both_return=True | No lock-order deadlock; prompt responses — _fail: request hangs/timeout_ | N1 |

### `GET /bookings`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-LIST-ORDER | 🔴 | 11 | List ascending by start_time | GET | 200 items=ascending start_time | Sorted asc start_time, ties asc id — _fail: descending_ | B5a |
| T-LIST-TIES |  | 11 | Equal start_time ties by ascending id | GET | 200 items=tie -> asc id | Ties broken by ascending id — _fail: tie order wrong_ |  |
| T-LIST-PAGE1 | 🔴 | 11 | Page 1 returns first slice | GET | 200 items[0]=first of ordering | page=1 -> items [0,10) — _fail: skips first 10_ | B5b |
| T-LIST-PAGE2 |  | 11 | Sequential pages never skip/repeat | SEQUENCE | 200 no_overlap_no_gap=True | Page2 continues exactly after page1 — _fail: overlap or gap_ |  |
| T-LIST-LIMIT | 🔴 | 11 | Limit honored | GET | 200 items_len=2 | Returns exactly limit items — _fail: returns up to 10_ | B5c |
| T-LIST-LIMIT-MAX |  | 11 | limit>100 -> 422 | GET | 422 detail=list | limit max is 100 — _fail: 200 with >100_ |  |
| T-LIST-TOTAL |  | 11 | total is full unpaginated count | GET | 200 total=N | total equals caller's booking count — _fail: wrong total_ |  |
| T-VIS-LIST-OWN | 🔴 | 10 | List shows only caller's bookings | GET | 200 items=only caller's | Member sees only own bookings — _fail: other users' bookings present_ |  |

### `GET /bookings/{id}`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-DETAIL-STARTTIME | 🔴 | 10 | Detail start_time is the booking start | GET | 200 start_time=== booked start | Detail returns real start_time — _fail: equals created_at_ | B7 |
| T-DETAIL-REFUNDS |  | 6 | Detail includes refunds array | GET | 200 refunds | Cancelled booking detail lists refund entries — _fail: missing/wrong shape_ |  |
| T-VIS-IDOR-GET | 🔴 | 10 | Member cannot read another's booking -> 404 | GET | 404 code=BOOKING_NOT_FOUND | Other member's booking id is 404 — _fail: 200_ | B6 |
| T-VIS-ADMIN-GET |  | 10 | Admin can read any org booking | GET | 200 | Admin reads any booking in org — _fail: 404_ |  |
| T-TENANT-BOOKING | 🔴 | 9 | Cross-org booking id -> 404 | GET | 404 code=BOOKING_NOT_FOUND | Foreign-org booking non-existent — _fail: 200/leak_ |  |

### `POST /bookings/{id}/cancel`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-REFUND-100 |  | 6 | >=48h notice -> 100% | POST | 200 refund_percent=100 | Full refund for >=48h notice — _fail: other_ |  |
| T-REFUND-48 | 🔴 | 6 | Exactly 48h notice -> 100% | POST | 200 refund_percent=100 | 48h boundary inclusive for 100% — _fail: 50_ | B8a |
| T-REFUND-50 |  | 6 | 24-48h notice -> 50% | POST | 200 refund_percent=50 | Half refund in [24,48) — _fail: other_ |  |
| T-REFUND-24 |  | 6 | Exactly 24h notice -> 50% | POST | 200 refund_percent=50 | 24h boundary inclusive for 50% — _fail: 0_ |  |
| T-REFUND-0 | 🔴 | 6 | <24h notice -> 0% | POST | 200 refund_percent=0 | No refund under 24h — _fail: 50_ | B8b |
| T-REFUND-ROUND | 🔴 | 6 | Half-cent rounds up | POST | 200 refund_amount_cents=501 | 50% of 1001 = 501 (half up) — _fail: 500_ | B9 |
| T-REFUND-CONSISTENT | 🔴 | 6 | Response amount == RefundLog amount | COMPARE | — equal=True | Returned refund equals stored RefundLog — _fail: differ_ | B9 |
| T-CANCEL-ONE-REFUNDLOG |  | 6 | Exactly one RefundLog per cancel | SEQUENCE | 200 refunds_len=1 | A cancelled booking has exactly one RefundLog — _fail: 0 or >1_ |  |
| T-CANCEL-DUP | 🔴 | 6 | Re-cancel -> 409 | POST | 409 code=ALREADY_CANCELLED | Cancelling twice rejected — _fail: other_ |  |
| T-CANCEL-AUTH | 🔴 | 10 | Non-owner member cannot cancel -> 404 | POST | 404 code=BOOKING_NOT_FOUND | Only owner or org admin may cancel — _fail: 200_ |  |
| T-CANCEL-ADMIN |  | 6 | Admin can cancel any org booking | POST | 200 status=cancelled | Admin cancels member's booking — _fail: 404_ |  |
| T-CANCEL-CONC | 🔴 | 6 | Concurrent cancel -> single refund | CONCURRENT | — refundlog_count=1 | Only one cancel succeeds; exactly one RefundLog — _fail: double refund/log_ | B-CONC |

### `GET /admin/usage-report`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-REPORT |  | 12 | Per-room usage report | GET | 200 from=str | Counts+revenue of confirmed bookings in [from,to] — _fail: wrong sums_ |  |
| T-REPORT-ZERO-ROOMS | 🔴 | 12 | Rooms with zero bookings included | GET | 200 includes_zero_rooms=True | Every org room appears even with 0 bookings — _fail: zero-rooms omitted_ |  |
| T-REPORT-EXCL-CANCEL |  | 12 | Cancelled excluded from report | GET | 200 excludes_cancelled=True | Only confirmed counted — _fail: cancelled counted_ |  |
| T-REPORT-RANGE |  | 12 | Date range inclusive [from,to] UTC | GET | 200 boundary_dates_included=True | Bookings on from and to dates included — _fail: boundary excluded_ |  |
| T-REPORT-STALE | 🔴 | 12 | Report reflects new booking immediately | SEQUENCE | 200 reflects_new_booking=True | Report is not stale after create — _fail: unchanged (stale cache)_ | AD1 |
| T-REPORT-ADMIN-ONLY | 🔴 | 12 | Member cannot access report -> 403 | GET | 403 code=FORBIDDEN | Admin-only endpoint — _fail: 200_ |  |
| T-TENANT-REPORT |  | 9 | Report only covers own org | GET | 200 only_own_org_rooms=True | No foreign-org rooms in report — _fail: foreign rooms present_ |  |

### `GET /admin/export`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-EXPORT-HEADER | 🔴 | 6 | CSV header exact | GET | 200 header=id,reference_code,room_id,user_id,start_time,end_time,status,price_cents | Exact CSV header order — _fail: wrong header_ |  |
| T-EXPORT-CROSSORG | 🔴 | 9 | Export cannot leak other org | GET | 404 code=ROOM_NOT_FOUND | Foreign-org room export blocked; no rows leak — _fail: org2 rows returned_ | EX1 |
| T-EXPORT-ADMIN-ONLY | 🔴 | 9 | Member cannot export -> 403 | GET | 403 code=FORBIDDEN | Admin-only endpoint — _fail: 200_ |  |

### `GET /health`

| ID | Crit | Rule | Title | Method | Expect | Behavior / Failure signal | Bug |
|----|:---:|:---:|-------|--------|--------|---------------------------|-----|
| T-HEALTH |  | 16 | Health endpoint ok | GET | 200 status=ok | Liveness returns {status: ok} — _fail: non-200/wrong body_ |  |

## Top critical cases (most likely to expose planted bugs)

- **T-REG-DUP** (rule 15, A4) — Duplicate username -> 409 USERNAME_TAKEN
- **T-LOGIN-BAD** (rule 8) — Bad credentials -> 401
- **T-AUTH-REFRESH-REUSE** (rule 8, A5) — Refresh token single-use
- **T-AUTH-LOGOUT** (rule 8, A2) — Logout invalidates presented access token
- **T-JWT-EXP** (rule 8, A1) — Access token exp-iat == 900s
- **T-JWT-CLAIMS** (rule 8) — Access token carries required claims
- **T-AUTH-MISSING** (rule 8) — No token on protected route -> 401
- **T-ROOM-CREATE-FORBIDDEN** (rule 9) — Member cannot create room -> 403
- **T-ROOMS-LIST-TENANT** (rule 9) — Room list is org-scoped
- **T-AVAIL-STALE** (rule 13, RM1) — Cancel reflected in availability
- **T-TENANT-ROOM** (rule 9) — Cross-org room id -> 404
- **T-STATS-DERIVED** (rule 14, S1) — Stats equal DB-derived values
- **T-STATS-CONC** (rule 14) — Stats consistent after concurrent bursts
- **T-WIN-ZERO** (rule 2, B3) — end == start -> 400
- **T-WIN-NEG** (rule 2, B3) — end < start -> 400
- **T-WIN-PAST** (rule 2, B2) — Past start (no grace) -> 400
- **T-TZ-OFFSET** (rule 1, T1) — Offset input converted to UTC
- **T-CONF-BACK2BACK** (rule 3, B1) — Back-to-back allowed
- **T-CONF-CONC** (rule 3, B-CONC) — No double-book under concurrency
- **T-QUOTA** (rule 4) — 4th booking in window -> 409
