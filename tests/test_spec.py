"""Visible, editable spec-reproduction tests (deterministic, in-process).

Each test asserts the BEHAVIOR REQUIRED BY THE PROBLEM STATEMENT (business rules
1-16). On the unfixed code many of these FAIL — that failure is the reproduction
of a planted bug. IDs in comments map to TESTCASES.md / TESTCASES.json and
BUG_LEDGER.md. Run: ``pytest tests/test_spec.py -q``.

Concurrency rules (3,4,5,7,16 "under concurrent requests") are covered separately
in tests/test_concurrency.py.
"""
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------- helpers
def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def future(hours=0, minutes=0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours, minutes=minutes)


def new_org() -> str:
    return "org-" + uuid.uuid4().hex[:10]


def register(org, user, pw="pw12345"):
    return client.post("/auth/register", json={"org_name": org, "username": user, "password": pw})


def login(org, user, pw="pw12345"):
    return client.post("/auth/login", json={"org_name": org, "username": user, "password": pw})


def auth(tok):
    return {"Authorization": f"Bearer {tok}"}


def admin_ctx():
    """Return (org, admin_token)."""
    org = new_org()
    register(org, "admin")
    tok = login(org, "admin").json()["access_token"]
    return org, tok


def member_ctx(org):
    """Register + login a fresh member in an existing org. Return token."""
    uname = "m-" + uuid.uuid4().hex[:8]
    register(org, uname)
    return login(org, uname).json()["access_token"], uname


def make_room(tok, rate=1000):
    r = client.post("/rooms", json={"name": "R", "capacity": 4, "hourly_rate_cents": rate}, headers=auth(tok))
    return r.json()["id"]


def book(tok, room, start, end):
    return client.post(
        "/bookings",
        json={"room_id": room, "start_time": iso(start), "end_time": iso(end)},
        headers=auth(tok),
    )


def decode(token):
    return jwt.decode(token, options={"verify_signature": False})


# ---------------------------------------------------------------- Rule 16 / health
def test_health():  # T-HEALTH
    assert client.get("/health").json() == {"status": "ok"}


# ---------------------------------------------------------------- Rule 15 / registration
def test_register_admin_then_member_roles():  # T-REG-ADMIN / T-REG-MEMBER
    org = new_org()
    a = register(org, "admin")
    assert a.status_code == 201 and a.json()["role"] == "admin"
    m = register(org, "bob")
    assert m.status_code == 201 and m.json()["role"] == "member"


def test_register_duplicate_username_409():  # T-REG-DUP  (bug A4)
    org = new_org()
    register(org, "dup")
    r = register(org, "dup")
    assert r.status_code == 409
    assert r.json()["code"] == "USERNAME_TAKEN"


# ---------------------------------------------------------------- Rule 8 / auth
def test_login_bad_credentials_401():  # T-LOGIN-BAD
    org = new_org()
    register(org, "u")
    r = client.post("/auth/login", json={"org_name": org, "username": "u", "password": "wrong"})
    assert r.status_code == 401 and r.json()["code"] == "INVALID_CREDENTIALS"


def test_access_token_lifetime_900s():  # T-JWT-EXP  (bug A1)
    _, tok = admin_ctx()
    p = decode(tok)
    assert p["exp"] - p["iat"] == 900


def test_jwt_required_claims():  # T-JWT-CLAIMS
    _, tok = admin_ctx()
    p = decode(tok)
    for claim in ("sub", "org", "role", "jti", "iat", "exp", "type"):
        assert claim in p, f"missing claim {claim}"
    assert isinstance(p["sub"], str)
    assert p["type"] == "access"


def test_refresh_token_lifetime_7d():  # T-JWT-REFRESH-EXP
    org, _ = admin_ctx()
    ref = login(org, "admin").json()["refresh_token"]
    p = decode(ref)
    assert p["exp"] - p["iat"] == 7 * 24 * 3600


def test_logout_invalidates_token():  # T-AUTH-LOGOUT  (bug A2)
    org, tok = admin_ctx()
    assert client.post("/auth/logout", headers=auth(tok)).status_code == 200
    # subsequent use of the same access token must be rejected
    assert client.get("/rooms", headers=auth(tok)).status_code == 401


def test_refresh_rotates():  # T-AUTH-REFRESH-ROTATE
    org, _ = admin_ctx()
    ref = login(org, "admin").json()["refresh_token"]
    r = client.post("/auth/refresh", json={"refresh_token": ref})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] and body["refresh_token"] and body["token_type"] == "bearer"


def test_refresh_single_use():  # T-AUTH-REFRESH-REUSE  (bug A5)
    org, _ = admin_ctx()
    ref = login(org, "admin").json()["refresh_token"]
    first = client.post("/auth/refresh", json={"refresh_token": ref})
    assert first.status_code == 200
    # reusing the now-consumed refresh token must fail
    second = client.post("/auth/refresh", json={"refresh_token": ref})
    assert second.status_code == 401


def test_missing_token_401():  # T-AUTH-MISSING
    assert client.get("/rooms").status_code == 401


# ---------------------------------------------------------------- Rule 1 / datetimes
def test_offset_input_converted_to_utc():  # T-TZ-OFFSET  (bug T1)
    _, tok = admin_ctx()
    room = make_room(tok)
    # pick a date far in the future so it is unambiguous
    r = client.post(
        "/bookings",
        json={"room_id": room, "start_time": "2027-03-01T12:00:00+06:00",
              "end_time": "2027-03-01T13:00:00+06:00"},
        headers=auth(tok),
    )
    assert r.status_code == 201
    # 12:00+06:00 == 06:00 UTC
    assert r.json()["start_time"].startswith("2027-03-01T06:00:00")


def test_naive_input_treated_as_utc():  # T-TZ-NAIVE
    _, tok = admin_ctx()
    room = make_room(tok)
    r = client.post(
        "/bookings",
        json={"room_id": room, "start_time": "2027-03-02T09:00:00",
              "end_time": "2027-03-02T10:00:00"},
        headers=auth(tok),
    )
    assert r.status_code == 201
    assert r.json()["start_time"].startswith("2027-03-02T09:00:00")


# ---------------------------------------------------------------- Rule 2 / price & window
def test_price_is_rate_times_hours():  # T-PRICE
    _, tok = admin_ctx()
    room = make_room(tok, rate=1000)
    r = book(tok, room, future(5), future(7))
    assert r.status_code == 201 and r.json()["price_cents"] == 2000


def test_duration_min_and_max_ok():  # T-WIN-MIN / T-WIN-MAX
    _, tok = admin_ctx()
    room = make_room(tok)
    assert book(tok, room, future(5), future(6)).status_code == 201       # 1h
    assert book(tok, room, future(10), future(18)).status_code == 201     # 8h


def test_duration_over_max_rejected():  # T-WIN-9H
    _, tok = admin_ctx()
    room = make_room(tok)
    assert book(tok, room, future(5), future(14)).status_code == 400      # 9h


def test_duration_non_whole_rejected():  # T-WIN-HALF
    _, tok = admin_ctx()
    room = make_room(tok)
    assert book(tok, room, future(5), future(6, 30)).status_code == 400   # 1.5h


def test_zero_duration_rejected():  # T-WIN-ZERO  (bug B3)
    _, tok = admin_ctx()
    room = make_room(tok)
    t = future(5)
    r = book(tok, room, t, t)
    assert r.status_code == 400 and r.json()["code"] == "INVALID_BOOKING_WINDOW"


def test_negative_duration_rejected():  # T-WIN-NEG  (bug B3)
    _, tok = admin_ctx()
    room = make_room(tok)
    r = book(tok, room, future(6), future(5))
    assert r.status_code == 400 and r.json()["code"] == "INVALID_BOOKING_WINDOW"


def test_past_start_rejected_no_grace():  # T-WIN-PAST  (bug B2)
    _, tok = admin_ctx()
    room = make_room(tok)
    r = book(tok, room, future(minutes=-1), future(minutes=59))
    assert r.status_code == 400 and r.json()["code"] == "INVALID_BOOKING_WINDOW"


# ---------------------------------------------------------------- Rule 3 / double-booking
def test_overlap_conflict():  # T-CONF-OVERLAP
    _, tok = admin_ctx()
    room = make_room(tok)
    assert book(tok, room, future(10), future(12)).status_code == 201
    r = book(tok, room, future(11), future(13))
    assert r.status_code == 409 and r.json()["code"] == "ROOM_CONFLICT"


def test_back_to_back_allowed():  # T-CONF-BACK2BACK  (bug B1)
    _, tok = admin_ctx()
    room = make_room(tok)
    base = future(10).replace(minute=0, second=0, microsecond=0)
    # exactly adjacent: first ends at `base+1h`, second starts at `base+1h`
    assert book(tok, room, base, base + timedelta(hours=1)).status_code == 201
    r = book(tok, room, base + timedelta(hours=1), base + timedelta(hours=2))
    assert r.status_code == 201


def test_cancelled_does_not_block():  # T-CONF-CANCELLED-IGNORED
    _, tok = admin_ctx()
    room = make_room(tok)
    b = book(tok, room, future(10), future(12))
    assert b.status_code == 201
    client.post(f"/bookings/{b.json()['id']}/cancel", headers=auth(tok))
    r = book(tok, room, future(10), future(12))
    assert r.status_code == 201


# ---------------------------------------------------------------- Rule 4 / quota
def test_quota_fourth_in_window_rejected():  # T-QUOTA
    org, _ = admin_ctx()
    tok, _ = member_ctx(org)
    a_tok = login(org, "admin").json()["access_token"]
    room = make_room(a_tok)
    # 3 bookings within (now, now+24h]
    for h in (2, 4, 6):
        assert book(tok, room, future(h), future(h + 1)).status_code == 201
    r = book(tok, room, future(8), future(9))
    assert r.status_code == 409 and r.json()["code"] == "QUOTA_EXCEEDED"


def test_quota_outside_window_ok():  # T-QUOTA-OUTSIDE
    org, _ = admin_ctx()
    tok, _ = member_ctx(org)
    a_tok = login(org, "admin").json()["access_token"]
    room = make_room(a_tok)
    for h in (2, 4, 6):
        assert book(tok, room, future(h), future(h + 1)).status_code == 201
    r = book(tok, room, future(30), future(31))  # beyond 24h
    assert r.status_code == 201


# ---------------------------------------------------------------- Rule 11 / pagination
def _seed_bookings(tok, room, n, base_h=5):
    ids = []
    for i in range(n):
        r = book(tok, room, future(base_h + 2 * i), future(base_h + 2 * i + 1))
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


def test_list_ascending_by_start_time():  # T-LIST-ORDER  (bug B5a)
    _, tok = admin_ctx()
    room = make_room(tok)
    _seed_bookings(tok, room, 3)
    items = client.get("/bookings", headers=auth(tok)).json()["items"]
    starts = [b["start_time"] for b in items]
    assert starts == sorted(starts)


def test_list_page_one_returns_first_slice():  # T-LIST-PAGE1  (bug B5b)
    _, tok = admin_ctx()
    room = make_room(tok)
    _seed_bookings(tok, room, 3)
    all_items = client.get("/bookings", headers=auth(tok), params={"page": 1, "limit": 100}).json()["items"]
    page1 = client.get("/bookings", headers=auth(tok), params={"page": 1, "limit": 2}).json()["items"]
    assert [b["id"] for b in page1] == [b["id"] for b in all_items[:2]]


def test_list_limit_honored():  # T-LIST-LIMIT  (bug B5c)
    _, tok = admin_ctx()
    room = make_room(tok)
    _seed_bookings(tok, room, 3)
    page = client.get("/bookings", headers=auth(tok), params={"limit": 2}).json()
    assert len(page["items"]) == 2


def test_list_total_is_full_count():  # T-LIST-TOTAL
    _, tok = admin_ctx()
    room = make_room(tok)
    _seed_bookings(tok, room, 3)
    assert client.get("/bookings", headers=auth(tok)).json()["total"] == 3


def test_list_only_callers_bookings():  # T-VIS-LIST-OWN
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    m_tok, _ = member_ctx(org)
    _seed_bookings(m_tok, room, 2, base_h=40)   # member's own (outside quota window)
    # admin has none on this fresh org
    assert client.get("/bookings", headers=auth(a_tok)).json()["total"] == 0
    assert client.get("/bookings", headers=auth(m_tok)).json()["total"] == 2


# ---------------------------------------------------------------- Rule 10 / visibility
def test_detail_start_time_correct():  # T-DETAIL-STARTTIME  (bug B7)
    _, tok = admin_ctx()
    room = make_room(tok)
    b = book(tok, room, future(5), future(6))
    bid = b.json()["id"]
    detail = client.get(f"/bookings/{bid}", headers=auth(tok)).json()
    assert detail["start_time"] == b.json()["start_time"]


def test_member_cannot_read_others_booking():  # T-VIS-IDOR-GET  (bug B6)
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    bob, _ = member_ctx(org)
    alice, _ = member_ctx(org)
    bid = book(bob, room, future(40), future(41)).json()["id"]
    r = client.get(f"/bookings/{bid}", headers=auth(alice))
    assert r.status_code == 404 and r.json()["code"] == "BOOKING_NOT_FOUND"


def test_admin_can_read_any_org_booking():  # T-VIS-ADMIN-GET
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    bob, _ = member_ctx(org)
    bid = book(bob, room, future(40), future(41)).json()["id"]
    assert client.get(f"/bookings/{bid}", headers=auth(a_tok)).status_code == 200


# ---------------------------------------------------------------- Rule 9 / multi-tenancy
def test_cross_org_room_is_404():  # T-TENANT-ROOM
    _, a1 = admin_ctx()
    _, a2 = admin_ctx()
    room2 = make_room(a2)
    r = client.get(f"/rooms/{room2}/availability", headers=auth(a1), params={"date": "2027-01-01"})
    assert r.status_code == 404 and r.json()["code"] == "ROOM_NOT_FOUND"


def test_cross_org_booking_is_404():  # T-TENANT-BOOKING
    _, a1 = admin_ctx()
    _, a2 = admin_ctx()
    room2 = make_room(a2)
    bid = book(a2, room2, future(5), future(6)).json()["id"]
    r = client.get(f"/bookings/{bid}", headers=auth(a1))
    assert r.status_code == 404


def test_booking_unknown_room_404():  # T-BOOK-ROOM-NOTFOUND
    _, a1 = admin_ctx()
    _, a2 = admin_ctx()
    room2 = make_room(a2)
    r = book(a1, room2, future(5), future(6))
    assert r.status_code == 404 and r.json()["code"] == "ROOM_NOT_FOUND"


def test_member_cannot_create_room():  # T-ROOM-CREATE-FORBIDDEN
    org, _ = admin_ctx()
    m_tok, _ = member_ctx(org)
    r = client.post("/rooms", json={"name": "X", "capacity": 2, "hourly_rate_cents": 500}, headers=auth(m_tok))
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN"


# ---------------------------------------------------------------- Rule 6 / refunds
def _booking_for_cancel(rate, start_dt):
    _, tok = admin_ctx()
    room = make_room(tok, rate=rate)
    b = book(tok, room, start_dt, start_dt + timedelta(hours=1))
    assert b.status_code == 201, b.text
    return tok, b.json()["id"]


def test_refund_100_percent():  # T-REFUND-100
    tok, bid = _booking_for_cancel(1000, future(50))
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.status_code == 200 and r.json()["refund_percent"] == 100


def test_refund_48h_boundary_is_100():  # T-REFUND-48  (bug B8a)
    tok, bid = _booking_for_cancel(1000, future(48, 30))  # >=48h notice
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.json()["refund_percent"] == 100


def test_refund_50_percent():  # T-REFUND-50
    tok, bid = _booking_for_cancel(1000, future(30))
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.json()["refund_percent"] == 50


def test_refund_under_24h_is_zero():  # T-REFUND-0  (bug B8b)
    tok, bid = _booking_for_cancel(1000, future(1))
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.json()["refund_percent"] == 0


def test_refund_half_cent_rounds_up():  # T-REFUND-ROUND  (bug B9)
    tok, bid = _booking_for_cancel(1001, future(30))  # 50% tier
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.json()["refund_amount_cents"] == 501  # 50% of 1001, half up


def test_refund_response_equals_refundlog():  # T-REFUND-CONSISTENT  (bug B9)
    tok, bid = _booking_for_cancel(1003, future(30))  # 50% tier; diverges under bug
    resp = client.post(f"/bookings/{bid}/cancel", headers=auth(tok)).json()
    detail = client.get(f"/bookings/{bid}", headers=auth(tok)).json()
    assert detail["refunds"], "expected a RefundLog entry"
    assert resp["refund_amount_cents"] == detail["refunds"][0]["amount_cents"]


def test_single_refundlog_per_cancel():  # T-CANCEL-ONE-REFUNDLOG
    tok, bid = _booking_for_cancel(1000, future(50))
    client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    detail = client.get(f"/bookings/{bid}", headers=auth(tok)).json()
    assert len(detail["refunds"]) == 1


def test_double_cancel_409():  # T-CANCEL-DUP
    tok, bid = _booking_for_cancel(1000, future(50))
    assert client.post(f"/bookings/{bid}/cancel", headers=auth(tok)).status_code == 200
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    assert r.status_code == 409 and r.json()["code"] == "ALREADY_CANCELLED"


def test_non_owner_member_cannot_cancel():  # T-CANCEL-AUTH
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    bob, _ = member_ctx(org)
    alice, _ = member_ctx(org)
    bid = book(bob, room, future(40), future(41)).json()["id"]
    r = client.post(f"/bookings/{bid}/cancel", headers=auth(alice))
    assert r.status_code == 404 and r.json()["code"] == "BOOKING_NOT_FOUND"


# ---------------------------------------------------------------- Rule 13 / availability
def test_availability_reflects_cancel():  # T-AVAIL-STALE  (bug RM1)
    _, tok = admin_ctx()
    room = make_room(tok)
    start = future(5).replace(minute=0, second=0, microsecond=0)
    date = start.date().isoformat()
    bid = book(tok, room, start, start + timedelta(hours=1)).json()["id"]
    # prime the availability cache
    before = client.get(f"/rooms/{room}/availability", headers=auth(tok), params={"date": date}).json()
    assert len(before["busy"]) == 1
    client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    after = client.get(f"/rooms/{room}/availability", headers=auth(tok), params={"date": date}).json()
    assert after["busy"] == []


# ---------------------------------------------------------------- Rule 12 / usage report
def test_report_reflects_new_booking():  # T-REPORT-STALE  (bug AD1)
    _, tok = admin_ctx()
    room = make_room(tok)
    start = future(5).replace(minute=0, second=0, microsecond=0)
    frm = to = start.date().isoformat()
    # prime the report cache (currently empty)
    first = client.get("/admin/usage-report", headers=auth(tok), params={"from": frm, "to": to}).json()
    assert first["rooms"][0]["confirmed_bookings"] == 0
    book(tok, room, start, start + timedelta(hours=1))
    second = client.get("/admin/usage-report", headers=auth(tok), params={"from": frm, "to": to}).json()
    assert second["rooms"][0]["confirmed_bookings"] == 1


def test_report_includes_zero_rooms_and_excludes_cancelled():  # T-REPORT-ZERO-ROOMS / EXCL-CANCEL
    _, tok = admin_ctx()
    r1 = make_room(tok)
    make_room(tok)  # zero-booking room
    start = future(5).replace(minute=0, second=0, microsecond=0)
    frm = to = start.date().isoformat()
    bid = book(tok, r1, start, start + timedelta(hours=1)).json()["id"]
    client.post(f"/bookings/{bid}/cancel", headers=auth(tok))
    rep = client.get("/admin/usage-report", headers=auth(tok), params={"from": frm, "to": to}).json()
    assert len(rep["rooms"]) == 2                       # zero-booking room present
    assert all(r["confirmed_bookings"] == 0 for r in rep["rooms"])  # cancelled excluded


def test_report_admin_only():  # T-REPORT-ADMIN-ONLY
    org, _ = admin_ctx()
    m_tok, _ = member_ctx(org)
    r = client.get("/admin/usage-report", headers=auth(m_tok), params={"from": "2027-01-01", "to": "2027-01-02"})
    assert r.status_code == 403


# ---------------------------------------------------------------- Rule 14 / stats
def test_stats_consistent_after_cancel():  # T-STATS-DERIVED  (bug S1)
    _, tok = admin_ctx()
    room = make_room(tok, rate=1000)
    b = book(tok, room, future(5), future(7))  # price 2000
    stats = client.get(f"/rooms/{room}/stats", headers=auth(tok)).json()
    assert stats["total_confirmed_bookings"] == 1 and stats["total_revenue_cents"] == 2000
    client.post(f"/bookings/{b.json()['id']}/cancel", headers=auth(tok))
    stats2 = client.get(f"/rooms/{room}/stats", headers=auth(tok)).json()
    assert stats2["total_confirmed_bookings"] == 0 and stats2["total_revenue_cents"] == 0


# ---------------------------------------------------------------- admin export
def test_export_header_exact():  # T-EXPORT-HEADER
    _, tok = admin_ctx()
    r = client.get("/admin/export", headers=auth(tok))
    header = r.text.splitlines()[0]
    assert header == "id,reference_code,room_id,user_id,start_time,end_time,status,price_cents"


def test_export_cannot_leak_other_org():  # T-EXPORT-CROSSORG  (bug EX1)
    _, a1 = admin_ctx()
    _, a2 = admin_ctx()
    room2 = make_room(a2)
    book(a2, room2, future(5), future(6))
    r = client.get("/admin/export", headers=auth(a1), params={"include_all": "true", "room_id": room2})
    # cross-org room must not leak org2 data: 404, or at least zero data rows
    if r.status_code == 200:
        data_rows = [ln for ln in r.text.splitlines()[1:] if ln.strip()]
        assert data_rows == [], "cross-org export leaked rows"
    else:
        assert r.status_code == 404


def test_export_admin_only():  # T-EXPORT-ADMIN-ONLY
    org, _ = admin_ctx()
    m_tok, _ = member_ctx(org)
    assert client.get("/admin/export", headers=auth(m_tok)).status_code == 403
