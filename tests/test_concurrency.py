"""Concurrency reproductions for rules 3, 4, 5, 7, 16.

FastAPI runs sync endpoints in a threadpool, so firing requests from a
ThreadPoolExecutor exercises the real race windows. These assert the invariants
that must hold "under concurrent requests"; on the unfixed code they fail
(duplicate reference codes, double-bookings, quota/limit bypass, or a deadlock
hang). IDs map to TESTCASES: T-REF-UNIQUE, T-CONF-CONC, T-QUOTA-CONC,
T-RATE-CONC, T-LIVENESS-DEADLOCK, T-STATS-CONC.
"""
import concurrent.futures as cf
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------- helpers
def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def future(hours=0, minutes=0):
    return datetime.now(timezone.utc) + timedelta(hours=hours, minutes=minutes)


def auth(tok):
    return {"Authorization": f"Bearer {tok}"}


def admin_ctx():
    org = "org-" + uuid.uuid4().hex[:10]
    client.post("/auth/register", json={"org_name": org, "username": "admin", "password": "pw12345"})
    tok = client.post("/auth/login", json={"org_name": org, "username": "admin", "password": "pw12345"}).json()["access_token"]
    return org, tok


def member_ctx(org):
    uname = "m-" + uuid.uuid4().hex[:8]
    client.post("/auth/register", json={"org_name": org, "username": uname, "password": "pw12345"})
    return client.post("/auth/login", json={"org_name": org, "username": uname, "password": "pw12345"}).json()["access_token"]


def make_room(tok, rate=1000):
    return client.post("/rooms", json={"name": "R", "capacity": 4, "hourly_rate_cents": rate}, headers=auth(tok)).json()["id"]


def book(tok, room, start, end):
    return client.post(
        "/bookings",
        json={"room_id": room, "start_time": iso(start), "end_time": iso(end)},
        headers=auth(tok),
    )


def run_parallel(fns, timeout=60):
    with cf.ThreadPoolExecutor(max_workers=len(fns)) as ex:
        futs = [ex.submit(fn) for fn in fns]
        return [f.result(timeout=timeout) for f in futs]


# ---------------------------------------------------------------- Rule 7
def test_reference_codes_unique_under_concurrency():  # T-REF-UNIQUE (REF1)
    _, tok = admin_ctx()
    room = make_room(tok)
    # distinct non-overlapping slots beyond the 24h quota window
    reqs = [(lambda h=h: book(tok, room, future(25 + 2 * h), future(26 + 2 * h))) for h in range(10)]
    results = run_parallel(reqs)
    assert all(r.status_code == 201 for r in results), [r.status_code for r in results]
    codes = [r.json()["reference_code"] for r in results]
    assert len(set(codes)) == len(codes), f"duplicate reference codes: {codes}"


# ---------------------------------------------------------------- Rule 3
def test_no_double_booking_under_concurrency():  # T-CONF-CONC (B-CONC)
    _, tok = admin_ctx()
    room = make_room(tok)
    start, end = future(30), future(31)  # identical slot for everyone
    reqs = [(lambda: book(tok, room, start, end)) for _ in range(8)]
    results = run_parallel(reqs)
    successes = [r for r in results if r.status_code == 201]
    conflicts = [r for r in results if r.status_code == 409]
    assert len(successes) == 1, f"double-booked: {[r.status_code for r in results]}"
    assert len(conflicts) == len(results) - 1


# ---------------------------------------------------------------- Rule 4
def test_quota_under_concurrency():  # T-QUOTA-CONC (B-CONC)
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    tok = member_ctx(org)
    # already holds 2 confirmed bookings in (now, now+24h]
    for h in (2, 4):
        assert book(tok, room, future(h), future(h + 1)).status_code == 201
    # fire 5 concurrent bookings at distinct in-window slots
    reqs = [(lambda h=h: book(tok, room, future(h), future(h + 1))) for h in (6, 8, 10, 12, 14)]
    run_parallel(reqs)
    # never more than 3 confirmed in the window
    listing = client.get("/bookings", headers=auth(tok), params={"limit": 100}).json()
    in_window = [b for b in listing["items"] if b["status"] == "confirmed"]
    assert len(in_window) <= 3, f"quota exceeded: {len(in_window)} confirmed in window"


# ---------------------------------------------------------------- Rule 5
def test_rate_limit_under_concurrency():  # T-RATE-CONC (RL1)
    org, a_tok = admin_ctx()
    room = make_room(a_tok)
    tok = member_ctx(org)
    # 30 concurrent requests; at most 20 may avoid the limiter
    reqs = [(lambda h=h: book(tok, room, future(30 + h), future(31 + h))) for h in range(30)]
    results = run_parallel(reqs)
    non_limited = [r for r in results if r.status_code != 429]
    assert len(non_limited) <= 20, f"rate limit bypassed: {len(non_limited)} passed"


# ---------------------------------------------------------------- Rule 16
def test_no_deadlock_on_concurrent_create_and_cancel():  # T-LIVENESS-DEADLOCK (N1)
    _, tok = admin_ctx()
    room = make_room(tok)
    # seed bookings we will cancel, at distinct slots beyond the quota window
    seeded = []
    for h in range(6):
        r = book(tok, room, future(40 + 2 * h), future(41 + 2 * h))
        assert r.status_code == 201
        seeded.append(r.json()["id"])

    def do_cancel(bid):
        return client.post(f"/bookings/{bid}/cancel", headers=auth(tok)).status_code

    def do_create(h):
        return book(tok, room, future(80 + 2 * h), future(81 + 2 * h)).status_code

    fns = []
    for bid in seeded:
        fns.append(lambda bid=bid: do_cancel(bid))
    for h in range(6):
        fns.append(lambda h=h: do_create(h))
    # if the notification lock-ordering deadlock regresses, result() times out
    results = run_parallel(fns, timeout=30)
    assert all(code in (200, 201) for code in results), results


# ---------------------------------------------------------------- Rule 14
def test_stats_consistent_under_concurrency():  # T-STATS-CONC (S1)
    _, tok = admin_ctx()
    room = make_room(tok, rate=1000)
    reqs = [(lambda h=h: book(tok, room, future(25 + 2 * h), future(26 + 2 * h))) for h in range(6)]
    results = run_parallel(reqs)
    ok = sum(1 for r in results if r.status_code == 201)
    stats = client.get(f"/rooms/{room}/stats", headers=auth(tok)).json()
    assert stats["total_confirmed_bookings"] == ok
    assert stats["total_revenue_cents"] == ok * 1000
