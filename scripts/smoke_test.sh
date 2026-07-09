#!/usr/bin/env bash
# Smoke test for a RUNNING CoWork API (local uvicorn or the Docker container).
# Usage:  BASE_URL=http://localhost:8000 ./scripts/smoke_test.sh
# Exits non-zero on the first failed check. Uses only python3 stdlib (no curl/jq).
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8000}"

BASE_URL="$BASE_URL" python3 - <<'PY'
import json, os, sys, urllib.request, urllib.error, uuid

B = os.environ["BASE_URL"].rstrip("/")
fails = []

def call(method, path, body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(B + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def check(name, cond):
    print(f"{'ok ' if cond else 'FAIL'}  {name}")
    if not cond:
        fails.append(name)

org = "smoke-" + uuid.uuid4().hex[:8]

s, b = call("GET", "/health")
check("health 200 {status: ok}", s == 200 and json.loads(b) == {"status": "ok"})

s, b = call("POST", "/auth/register", {"org_name": org, "username": "admin", "password": "pw12345"})
check("register admin 201", s == 201 and json.loads(b)["role"] == "admin")

s, b = call("POST", "/auth/login", {"org_name": org, "username": "admin", "password": "pw12345"})
check("login 200", s == 200)
tok = json.loads(b)["access_token"]

s, b = call("POST", "/rooms", {"name": "R", "capacity": 4, "hourly_rate_cents": 1000}, tok)
check("create room 201", s == 201)
rid = json.loads(b)["id"]

# offset datetime must be converted to UTC (rule 1)
s, b = call("POST", "/bookings",
            {"room_id": rid, "start_time": "2027-05-01T12:00:00+06:00", "end_time": "2027-05-01T13:00:00+06:00"}, tok)
ok = s == 201 and json.loads(b)["start_time"].startswith("2027-05-01T06:00:00") and json.loads(b)["price_cents"] == 1000
check("booking 201, offset->UTC, price=1000", ok)

# malformed datetime must be a clean 400, not a 500 (H1)
s, b = call("POST", "/bookings", {"room_id": rid, "start_time": "nope", "end_time": "2027-05-01T13:00:00"}, tok)
check("malformed datetime -> 400", s == 400 and json.loads(b).get("code") == "INVALID_BOOKING_WINDOW")

# duplicate username -> 409 (rule 15)
s, b = call("POST", "/auth/register", {"org_name": org, "username": "admin", "password": "pw12345"})
check("duplicate username -> 409", s == 409 and json.loads(b).get("code") == "USERNAME_TAKEN")

print()
if fails:
    print(f"SMOKE FAILED: {len(fails)} check(s) failed")
    sys.exit(1)
print("SMOKE PASSED")
PY
