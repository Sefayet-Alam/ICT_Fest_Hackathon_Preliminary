# TESTCASES — CoWork Booking API (visible & editable)

Black-box tests derived from `README.md` business rules. Base URL `http://localhost:8000`.
Each case is human-runnable (curl) and mirrored in `TESTCASES.json`.
Status: `untested` | `pass` | `fail`. Edit freely — these are yours, not hidden pytest.

**Auth setup used by most cases** (`$ADMIN`, `$MEMBER`, `$ROOM` refer to values captured from earlier steps):
```bash
# admin (creates org)
curl -s localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"admin","password":"pw12345"}'
ADMIN=$(curl -s localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"admin","password":"pw12345"}' | jq -r .access_token)
# member (joins same org)
curl -s localhost:8000/auth/register -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"bob","password":"pw12345"}'
MEMBER=$(curl -s localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"org_name":"acme","username":"bob","password":"pw12345"}' | jq -r .access_token)
ROOM=$(curl -s localhost:8000/rooms -H "Authorization: Bearer $ADMIN" -H 'Content-Type: application/json' \
  -X POST -d '{"name":"Focus","capacity":4,"hourly_rate_cents":1000}' | jq -r .id)
```

---

| ID | Title | Purpose | Setup | Request / Action | Expected result | Failure signal | Notes |
|----|-------|---------|-------|------------------|-----------------|----------------|-------|
| T-HEALTH | Health check | Liveness | none | `GET /health` | 200 `{"status":"ok"}` | non-200 or wrong body | baseline |
| T-REG-ADMIN | Register creates org admin | Rule 15 | none | `POST /auth/register {acme2,alice,pw}` | 201, `role":"admin"` | role≠admin | first user in new org |
| T-REG-MEMBER | Join existing org as member | Rule 15 | org exists | `POST /auth/register {acme,bob2,pw}` | 201, `role":"member"` | role≠member | |
| T-REG-DUP | Duplicate username → 409 | Rule 15 / **A4** | user exists | register same org+username twice | 409 `USERNAME_TAKEN` | 200 or 500 | currently returns 200 |
| T-LOGIN-BAD | Bad credentials | contract | user exists | `POST /auth/login` wrong pw | 401 `INVALID_CREDENTIALS` | other status | |
| T-JWT-EXP | Access token lifetime = 900s | Rule 8 / **A1** | login | decode access token; `exp − iat` | exactly 900 | 54000 or other | decode JWT payload |
| T-AUTH-LOGOUT | Logout invalidates token | Rule 8 / **A2** | login | `POST /auth/logout` then reuse same token on `GET /rooms` | reuse → 401 | 200 after logout | |
| T-AUTH-REFRESH-ROTATE | Refresh returns new pair | Rule 8 | login | `POST /auth/refresh {refresh}` | 200 new access+refresh | non-200 | |
| T-AUTH-REFRESH-REUSE | Refresh single-use | Rule 8 / **A5** | refreshed once | reuse the old refresh token | 401 | 200 (reusable) | |
| T-TZ-OFFSET | Offset input → UTC | Rule 1 / **T1** | admin, room | book `start=2026-12-01T12:00:00+06:00`,`end=...T13:00:00+06:00`; GET availability for `2026-12-01` | busy shows `06:00:00Z` start | shows `12:00` (offset dropped) | whole instant shifts 6h |
| T-WIN-PAST | Past start rejected (no grace) | Rule 2 / **B2** | admin, room | book start = now−60s | 400 `INVALID_BOOKING_WINDOW` | 201 | current 300s grace |
| T-WIN-ZERO | Zero duration rejected | Rule 2 / **B3** | admin, room | book start==end | 400 `INVALID_BOOKING_WINDOW` | 201 price 0 | |
| T-WIN-NEG | end<start rejected | Rule 2 / **B3** | admin, room | book end 1h before start | 400 `INVALID_BOOKING_WINDOW` | 201/negative price | |
| T-WIN-9H | Duration 9h rejected | Rule 2 | admin, room | book 9h span | 400 `INVALID_BOOKING_WINDOW` | 201 | max 8 |
| T-WIN-HALF | Non-whole hours rejected | Rule 2 | admin, room | book 1.5h span | 400 `INVALID_BOOKING_WINDOW` | 201 | |
| T-PRICE | Price = rate × hours | Rule 2 | room rate 1000 | book 2h | 201 `price_cents":2000` | wrong price | |
| T-CONF-OVERLAP | Overlapping confirmed → 409 | Rule 3 | one booking 10–12 | book 11–13 same room | 409 `ROOM_CONFLICT` | 201 | true overlap |
| T-CONF-BACK2BACK | Back-to-back allowed | Rule 3 / **B1** | one booking 10–11 | book 11–12 same room | 201 | 409 | **key bug** |
| T-QUOTA | 4th booking in 24h window → 409 | Rule 4 | 3 confirmed in (now,+24h] | create 4th | 409 `QUOTA_EXCEEDED` | 201 | across rooms in org |
| T-QUOTA-OUTSIDE | Booking >24h out not quota-limited | Rule 4 | 3 in window | book start now+30h | 201 | 409 | window is (now,+24h] |
| T-LIST-ORDER | List ascending by start_time | Rule 11 / **B5a** | ≥2 bookings | `GET /bookings` | ascending start_time | descending | |
| T-LIST-PAGE1 | Page 1 returns first slice | Rule 11 / **B5b** | ≥11 bookings | `GET /bookings?page=1&limit=10` | items[0..10) of ordering | skips first 10 | off-by-one |
| T-LIST-LIMIT | Limit honored | Rule 11 / **B5c** | ≥3 bookings | `GET /bookings?limit=2` | exactly 2 items | returns up to 10 | |
| T-LIST-TOTAL | total is full count | Rule 11 | N bookings | `GET /bookings` | `total`=N | wrong total | |
| T-VIS-IDOR-GET | Member can't read other's booking | Rule 10 / **B6** | bob books; alice(member) | alice `GET /bookings/{bobBooking}` | 404 `BOOKING_NOT_FOUND` | 200 | IDOR |
| T-VIS-ADMIN-GET | Admin reads any org booking | Rule 10 | bob books | admin `GET /bookings/{bobBooking}` | 200 | 404 | |
| T-DETAIL-STARTTIME | Detail start_time correct | contract / **B7** | one booking | `GET /bookings/{id}` | start_time == booked start | equals created_at | |
| T-DETAIL-REFUNDS | Detail includes refunds array | contract | cancelled booking | `GET /bookings/{id}` | `refunds:[{amount_cents,status,processed_at}]` | missing/shape wrong | |
| T-REFUND-100 | ≥48h notice → 100% | Rule 6 | booking start now+50h | cancel | `refund_percent":100` | other | |
| T-REFUND-48 | Exactly 48h → 100% | Rule 6 / **B8a** | booking start now+48h | cancel | 100% | 50% | boundary |
| T-REFUND-50 | 24–48h → 50% | Rule 6 | booking start now+30h | cancel | 50% | other | |
| T-REFUND-0 | <24h → 0% | Rule 6 / **B8b** | booking start now+1h | cancel | 0% | 50% | **key bug** |
| T-REFUND-ROUND | Half-cent rounds up | Rule 6 / **B9** | price 1001, cancel 50% | cancel | `refund_amount_cents":501` | 500 | banker's/trunc bug |
| T-REFUND-CONSISTENT | Response == RefundLog | Rule 6 / **B9** | any cancel | compare cancel `refund_amount_cents` vs `GET /bookings/{id}` refunds[0].amount_cents | equal | differ | |
| T-CANCEL-DUP | Re-cancel → 409 | Rule 6 | cancelled booking | cancel again | 409 `ALREADY_CANCELLED` | other | |
| T-CANCEL-AUTH | Non-owner member can't cancel | Rule 6/10 | bob books; alice member | alice cancels bob's | 404 `BOOKING_NOT_FOUND` | 200 | |
| T-AVAIL | Availability lists busy | Rule 13 | booking on date D | `GET /rooms/{id}/availability?date=D` | busy interval present, sorted | missing/unsorted | |
| T-AVAIL-STALE | Cancel updates availability | Rule 13 / **RM1** | book, GET avail (caches), cancel | GET avail again | booking gone | still busy (stale cache) | |
| T-REPORT | Usage report per room | Rule 12 | bookings in range | `GET /admin/usage-report?from&to` | counts+revenue incl zero-booking rooms | missing rooms/wrong sums | |
| T-REPORT-STALE | Create updates report | Rule 12 / **AD1** | GET report (caches), create booking | GET report again | reflects new booking | stale (unchanged) | |
| T-REPORT-EXCL-CANCEL | Cancelled excluded from report | Rule 12 | cancelled booking | GET report | not counted | counted | |
| T-STATS-DERIVED | Stats equal DB-derived | Rule 14 / **S1** | create then cancel | `GET /rooms/{id}/stats` | count/revenue match live bookings | drift after cancel/concurrency | |
| T-EXPORT-HEADER | CSV header exact | contract | any | `GET /admin/export` | header `id,reference_code,room_id,user_id,start_time,end_time,status,price_cents` | wrong header | |
| T-EXPORT-CROSSORG | Export can't leak other org | Rule 9 / **EX1** | 2 orgs, room in org2 | org1 admin `GET /admin/export?include_all=true&room_id=<org2 room>` | no org2 rows (404 or empty) | org2 bookings leaked | **security** |
| T-TENANT-ROOM | Cross-org room id → 404 | Rule 9 | room in org2 | org1 user `GET /rooms/{org2room}/availability` | 404 `ROOM_NOT_FOUND` | 200/leak | |
| T-ADMIN-ONLY-CREATE | Member can't create room | contract | member token | `POST /rooms` as member | 403 `FORBIDDEN` | 201 | |
| T-REF-UNIQUE | Reference codes unique (concurrency) | Rule 7 / **REF1** | admin, room | fire 10 concurrent `POST /bookings` distinct slots | all reference_codes distinct | duplicates | needs concurrency runner |
| T-CONF-CONC | No double-book under concurrency | Rule 3 / **B-CONC** | admin, room | fire 5 concurrent identical-slot `POST /bookings` | exactly 1 × 201, rest 409 | ≥2 × 201 | |
| T-QUOTA-CONC | Quota holds under concurrency | Rule 4 / **B-CONC** | member at 3-in-window | fire concurrent 4th+5th | ≤ limit respected | >3 confirmed | |
| T-RATE | Rate limit 20/60s | Rule 5 | member | 21 sequential `POST /bookings` in <60s | 21st → 429 `RATE_LIMITED` | all 201 | count includes failures |
| T-RATE-CONC | Rate limit under concurrency | Rule 5 / **RL1** | member | fire 30 concurrent `POST /bookings` | ≤20 pass then 429 | >20 pass | |
| T-LIVENESS-DEADLOCK | No hang on concurrent create+cancel | Rule 16 / **N1** | booking exists | concurrently create one and cancel one | both return promptly | request hangs/timeout | deadlock |
| T-AUTH-MISSING | No token → 401 | Rule 8 | none | `GET /rooms` no header | 401 | other | |
| T-AUTH-EXPIRED | Expired/blacklisted token → 401 | Rule 8 | logged-out token | reuse | 401 | 200 | |

---

### Top 10 highest-value (most likely to expose planted bugs)
1. **T-CONF-BACK2BACK** (B1) — strict-vs-`<=` overlap.
2. **T-REFUND-0** (B8b) — <24h refunds 50% instead of 0%.
3. **T-VIS-IDOR-GET** (B6) — cross-member booking read.
4. **T-EXPORT-CROSSORG** (EX1) — cross-org data leak.
5. **T-LIST-PAGE1 / T-LIST-LIMIT / T-LIST-ORDER** (B5) — pagination trio.
6. **T-JWT-EXP** (A1) — token lifetime 54000s.
7. **T-AUTH-LOGOUT** (A2) — logout no-op.
8. **T-TZ-OFFSET** (T1) — timezone not converted.
9. **T-REFUND-ROUND / T-REFUND-CONSISTENT** (B9) — rounding + response≠ledger.
10. **T-LIVENESS-DEADLOCK** (N1) — notification deadlock hang.
