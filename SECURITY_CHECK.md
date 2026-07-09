# SECURITY_CHECK — CoWork Booking API

**Verdict: SAFE TO PUBLISH (secrets)** — no secrets, keys, `.env`, or DB files in
the repo. **One decision for you:** the problem-statement PDF is committed (see below).

## Secret handling
- No `.env` in the repo. No API keys, tokens, private keys, or DB dumps committed.
- `JWT_SECRET` is read from the environment with a **placeholder** default (`cowork-dev-secret-change-me`) in `app/config.py` — a non-secret dev default, not a real credential. The container/grader supplies the real value at runtime.
- Passwords: PBKDF2-HMAC-SHA256 with a per-user random salt (`app/auth.py`). No plaintext.
- Test fixtures use obvious placeholders (`pw12345`, `test-secret`). No real credentials hardcoded.
- Secret-pattern scan over all tracked text files: only field-name references in spec/tests — **no secret values**.

## .env / .gitignore status
- `.gitignore` excludes `__pycache__/`, `*.pyc`, `*.db`, `.venv/`, `venv/`, `.pytest_cache/`.
- Verified ignored: `.venv/`, `cowork.db` (runtime DB never committed).
- Optional hardening: add `.env`/`*.env` to `.gitignore` and ship a `.env.example` with `JWT_SECRET=change-me` so evaluators know the required var. Not required for safety (no `.env` exists).

## Decision needed — committed problem statement
- `docs/ICT_Fest_Hackathon_Preliminary.pdf` was committed (commit "Add pdf for documentation"). The submission repo must be **public**, so this PDF becomes public too.
- If the organizers intend the problem statement to be public, keeping it is fine. If not, remove it before pushing:
  ```bash
  git rm docs/ICT_Fest_Hackathon_Preliminary.pdf
  echo "*.pdf" >> .gitignore
  git commit -m "chore: remove problem-statement PDF from public repo"
  ```
  (It only lives in the last commit, so no history rewrite is needed if removed before push. If it has already been pushed, rewrite history.)

## Auth / data-isolation (these were graded BUGS — now FIXED, listed for completeness)
- Cross-org export leak (EX1) — fixed: export is org-scoped, cross-org room → 404.
- Booking IDOR (B6) — fixed: members only read their own bookings.
- Logout no-op (A2) / refresh reuse (A5) — fixed: `jti` blacklist + single-use rotation.
- All multi-tenancy paths return 404 for cross-org ids.

## Public-repo safety checklist
- [x] No secrets in tracked files (scanned)
- [x] `.gitignore` covers db/venv/cache; `.venv` and `cowork.db` confirmed ignored
- [x] No hardcoded real credentials; passwords hashed
- [x] Git history clean of secrets (only source + docs + PDF commits)
- [ ] **Decide on `docs/…​.pdf`** (keep vs remove) before pushing public
- [ ] Optional: add `.env` to `.gitignore` + `.env.example`
- [ ] Final `git status` clean of stray local/large files
