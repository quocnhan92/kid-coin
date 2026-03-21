## KidCoin - Production Deploy Checklist (Next Few Days)

This checklist is tailored to the current KidCoin codebase (FastAPI + SQLAlchemy, current startup seeding, docker-compose aimed at dev).

### Acceptance Criteria (what "done" means)
- App runs reliably in staging/production with correct configuration via env vars.
- Database schema is managed by migrations (Alembic) and is reproducible from scratch.
- Authentication is secure enough for production (no demo fallbacks, no plaintext secrets/pins).
- Critical flows are tested (quests approve/reject, reward redeem/delivery, club leaderboard).
- Observability exists: structured logs, request IDs, error tracking signals, health endpoints.
- CI/CD can build and deploy the same artifact the team tested.

---

### Day 1: Configuration & Database Foundations
- [ ] Add a real `.env.example` and document required env vars.
- [ ] Remove hardcoded secrets (e.g. `SECRET_KEY="your-secret-key-here"`) from code; load via env only.
- [ ] Remove `Base.metadata.create_all(bind=engine)` from `main.py` (use migrations instead).
- [ ] Initialize Alembic for this project (create `alembic/` folder + `alembic.ini` + env config).
- [ ] Create initial migration(s) that match the current SQLAlchemy models.
- [ ] Add migration command docs (local + docker).
- [ ] Verify migrations work on a clean DB:
  - [ ] Start Postgres fresh
  - [ ] Run migrations
  - [ ] Start backend
- [ ] Decide seeding strategy for prod:
  - [ ] Remove automatic seeding on every startup
  - [ ] If seeding is needed, guard it (ENV flag) and/or make it idempotent

---

### Day 2: Docker & Deployment Mechanics
- [ ] Update `docker-compose.yml` for production:
  - [ ] Remove dev bind mount `- .:/app` from `web`
  - [ ] Use a production server command (no `--reload`)
  - [ ] Keep `db` network internal (no need to expose `5432` publicly)
- [ ] Ensure `DATABASE_URL` is consistent across containers (web uses `db` hostname).
- [ ] Add restart policies (e.g. `restart: unless-stopped`) for web/db.
- [ ] Add resource limits if needed (CPU/memory) to prevent host overload.
- [ ] Add a simple health check for the web service (e.g. GET `/api/v1/system/health` or `/health`).
- [ ] Document deploy commands (staging and production) in README or a new doc.

---

### Day 3: Security & Auth Hardening
- [ ] Remove the DEV auto-seed/fallback inside auth dependency (`deps.get_current_user`) and require explicit auth.
- [ ] Do not accept/compare PIN in plaintext:
  - [ ] Store hashed PIN (bcrypt/passlib) in DB
  - [ ] Verify PIN by hash compare
- [ ] Verify parent login logic:
  - [ ] `register-device` currently takes `password` but does not truly validate it against a persisted password/PIN policy
  - [ ] Implement proper verification strategy
- [ ] Protect cookie/session auth:
  - [ ] Set secure cookie flags (`httponly`, `secure`, `samesite`)
  - [ ] Add CSRF protection for state-changing endpoints (POST/PUT) if using cookies
- [ ] Add rate limiting for auth endpoints (device-status/register-device/quick-login).
- [ ] Validate inputs strictly (max lengths, allowed enum values) for request bodies.
- [ ] Ensure all endpoints that mutate data have auth checks and family_id isolation.

---

### Day 4: Data Integrity & Transaction Safety
- [ ] Ensure "quest submission once per day" is race-safe (consider DB constraints or SERIALIZABLE/locking).
- [ ] Ensure approving a quest is idempotent (avoid double-approve awarding coins twice).
- [ ] Ensure redeeming a reward is idempotent (avoid double-redeem deducting twice on retries).
- [ ] Add/verify DB constraints:
  - [ ] `TaskLog` check constraint for exactly one source task (family_task_id xor club_task_id) exists
  - [ ] Add NOT NULL/unique constraints where required (e.g. reference integrity, redemption status transitions)
- [ ] Confirm stock decrement cannot go negative (enforce via logic + optional DB constraint).

---

### Day 5: Testing, CI, and Staging Validation
- [ ] Add unit/integration tests:
  - [ ] Approve quest: creates Transaction + updates balances + updates TaskLog status
  - [ ] Reject quest: updates TaskLog status but does not award
  - [ ] Redeem reward: checks balance + creates RedemptionLog + creates Transaction + deducts coins + decrements stock
  - [ ] Delivery: updates RedemptionLog to DELIVERED
  - [ ] Club leaderboard: returns members sorted by XP
- [ ] Add a test DB strategy:
  - [ ] Use migrations to set up schema for tests
  - [ ] Use transaction rollback between tests or rebuild per test suite
- [ ] Add CI workflow:
  - [ ] Lint/format (if configured)
  - [ ] Run tests
  - [ ] Build docker image
- [ ] Add staging deploy:
  - [ ] Run migrations
  - [ ] Seed if required
  - [ ] Smoke test all endpoints + key UI screens

---

### Release Day: Operational Checklist
- [ ] Set final env vars in production (no default weak secrets).
- [ ] Run migrations and verify schema version.
- [ ] Start services and monitor logs for errors for at least 5-10 minutes.
- [ ] Verify audit_logs are created for critical actions.
- [ ] Validate payment/points invariants:
  - [ ] Coin never goes negative for KID
  - [ ] XP matches approved quests only
  - [ ] Reward stock decrement matches redemption count
- [ ] Provide rollback plan:
  - [ ] If deployment fails, revert to last working image
  - [ ] Keep migrations backward compatible or plan a rollback migration

---

### Smoke Test Commands (manual)
- [ ] `curl`/browser test: `/login` then device-status -> quick-login -> redirect
- [ ] `GET /api/v1/system/health`
- [ ] `GET /api/v1/quests/daily` as KID
- [ ] Submit a quest: `POST /api/v1/quests/{task_id}/submit`
- [ ] Approve quest: `POST /api/v1/quests/{log_id}/verify` with `{ "action": "APPROVE" }`
- [ ] Redeem reward: `POST /api/v1/rewards/{reward_id}/redeem`
- [ ] Deliver reward: `PUT /api/v1/rewards/delivery/{redemption_id}`
- [ ] Create/join club + leaderboard: endpoints under `/api/v1/clubs`

