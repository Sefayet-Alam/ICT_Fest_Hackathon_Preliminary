# SECURITY_CHECK — CoWork Booking API

**Verdict (current): SAFE TO PUBLISH** — no secrets or confidential files detected in the working tree. Re-run before final push.

## Secret handling
- No `.env` file present in the repo. No API keys, tokens, private keys, or DB dumps committed.
- `JWT_SECRET` is read from the environment with a **dev placeholder default** (`cowork-dev-secret-change-me`) in `app/config.py`. This is a non-secret placeholder, not a real credential — acceptable for a public repo. The grader supplies its own `JWT_SECRET` at container runtime.
- Passwords stored as PBKDF2-HMAC-SHA256 with per-user salt (`app/auth.py`) — no plaintext passwords.
- No hardcoded real credentials found.

## .env / .gitignore status
- `.gitignore` present and excludes: `__pycache__/`, `*.pyc`, `*.db`, `.venv/`, `venv/`, `.pytest_cache/`.
- **Recommendation (execution phase):** add `.env` and `*.env` to `.gitignore` defensively, and ship a `.env.example` with placeholder `JWT_SECRET=change-me` so evaluators know the required vars without exposing anything.
- SQLite DB file (`cowork.db`) is git-ignored via `*.db` — good, prevents committing runtime data.

## Confidential-data exposure checklist
- [x] No `.env` committed
- [x] No API keys / tokens / private keys in source
- [x] No database file committed (`*.db` ignored)
- [x] No hidden evaluation materials or grader files copied in
- [x] No hardcoded real secrets
- [x] Problem-statement PDF (`ICT_Fest_Hackathon_Preliminary.pdf`) lives in the **parent** workspace, NOT inside the challenge repo → will not be committed/published. Keep it out of the repo.
- [ ] Re-verify `git status` / `git diff` before public push (execution Phase 8)

## Auth / data-access risks (informational — these are the graded bugs, not repo-safety issues)
- Multi-tenancy: `/admin/export` currently leaks cross-org bookings (bug EX1) — a data-isolation defect to FIX in code (tracked in BUG_LEDGER). Not a repo-publishing risk.
- IDOR on `GET /bookings/{id}` (bug B6) — data-isolation defect to fix.
- Logout/refresh token invalidation broken (A2/A5) — auth defects to fix.
- These are correctness bugs the grader tests; fixing them is the task. They do not affect whether the *repository* is safe to make public.

## Public-repo safety checklist (pre-submission)
- [x] No secrets in tracked files
- [x] `.gitignore` covers db/venv/cache
- [ ] Add `.env` to `.gitignore` + provide `.env.example` (defensive)
- [ ] `git log`/history contains no secret (single initial commit + doc commits — clean)
- [ ] Confirm PDF/problem statement not added to repo
- [ ] Final `git status` clean of stray large/local files
