# NibblAI Backend

Django + DRF backend for the NibblAI rebate & review platform.

## Stack

- Python 3.13, Django 6.0, Django REST Framework
- PostgreSQL (no Celery/Redis yet — background jobs run as management commands for now)
- OpenAPI docs via drf-spectacular
- Dependency management via `uv`

## Project layout

```
core/                  # Django project (settings package, urls, wsgi/asgi)
  settings/            # base.py, dev.py, prod.py, test.py
Apps/                  # local apps live here
  common/              # shared base models (UUID/timestamps/soft-delete), AuditLog, health check
```

Each app follows: `models.py`, `api/` (views, urls), `services.py`, `selectors.py`,
`permissions.py`, `tests/`.

### Apps (M0–M15)

| App | Responsibility |
|-----|----------------|
| `common` | Base models (UUID/timestamps/soft-delete), `AuditLog`, money/text/date helpers, `DomainError`, `IsPlatformAdmin`, health check |
| `accounts` | Custom email `User`, JWT auth, email/phone verification, password reset, referrals, social-login seam |
| `brands` | Brand tenancy, applications/approval, memberships, the **Customers module** (plan-gated) |
| `billing` | Plans (Starter/Pro/Scale), subscriptions, per-plan fee computation |
| `wallets` | Append-only ledger, escrow holds, `WalletService` (credit/debit/hold/capture/release) |
| `products` | Product Library, alias matching, tag generator |
| `campaigns` | Rebate campaign config: tiers (=100%), restriction engine, fallback, QR/URL, preview, funding gate |
| `offers` | Consumer feed/discovery, bookmarks, best-offer resolution, 30-day cooldown |
| `reservations` | Claim→reserve lifecycle (7-day expiry, global cap, budget-by-sum) |
| `receipts` | Upload, OCR seam, product matching, duplicate/fraud detection, manual review queue |
| `rebates` | Reward issuance (capture hold + customer credit + brand fee) |
| `reviews` | AI review campaigns, rules engine, chat sessions, moderation |
| `notifications` | Device tokens, templates, preferences, reminders/re-engagement |
| `analytics` | Live brand/platform dashboards + idempotent snapshot rollups |
| `admin_panel` | Platform oversight, promo credits, user suspension, audit-log access |

### Background jobs (management commands)

No Celery yet — run these on cron until Celery Beat is introduced:

```bash
python manage.py charge_subscriptions      # monthly brand subscription charges
python manage.py sync_campaign_funding     # pause/resume campaigns by wallet funding
python manage.py expire_reservations       # expire 7-day reservations, release holds
python manage.py expire_review_sessions    # expire review opportunities
python manage.py release_held_reviews      # publish 1–2★ reviews after 30-day hold
python manage.py send_notifications        # reminders + re-engagement + new offers
python manage.py refresh_analytics         # recompute analytics snapshots
```

## Local setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Start PostgreSQL (Docker convenience — only the DB runs in a container):
   ```bash
   docker compose up -d db
   ```
   Or point `.env` at any existing Postgres.

3. Create your env file:
   ```bash
   cp .env.example .env
   ```

4. Migrate and run:
   ```bash
   uv run python manage.py migrate
   uv run python manage.py runserver
   ```

## Useful URLs

- Health check: `GET /api/v1/health/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`
- Django admin: `/admin/`

## Settings modules

- `core.settings.dev` — local development (default for `manage.py`)
- `core.settings.prod` — production (default for `wsgi`/`asgi`)
- `core.settings.test` — test runs

## Running tests

```bash
uv run python manage.py test --settings=core.settings.test
```

200 tests; 2 are Postgres-only concurrency tests (skipped on SQLite).

## Production notes

- **Settings:** `core.settings.prod` enables HSTS, SSL redirect, secure cookies,
  and `X-Forwarded-Proto`. Provide a strong `SECRET_KEY`, real `ALLOWED_HOSTS`,
  and `DATABASE_URL`/`DB_*` via the environment.
- **Throttling:** DRF rate limits via `anon` / `user` scopes plus a stricter
  `auth` scope on login/register/password/social endpoints. Backed by the cache
  (LocMem in dev → **use Redis in production**, see `CACHES`).
- **Idempotency:** all ledger writes accept idempotency keys; redemption/review/
  payout flows derive stable keys from domain ids, and the wallet-funding
  endpoint accepts a client `idempotency_key`.
- **Concurrency:** money operations lock the wallet/campaign row
  (`SELECT … FOR UPDATE`) on PostgreSQL.
- **Integration seams** (mocked, ready to wire): OCR provider (`receipts/ocr.py`),
  Claude prompts (`reviews/ai.py`), FCM push (`notifications/push.py`),
  PayPal/Venmo payouts (`payouts` `mark_paid`/export), S3 receipt storage.
- **Deploy check:** `python manage.py check --deploy --settings=core.settings.prod`.

### Secrets & Environment Variables

See the detailed guides:
- **[SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md)** — How to manage API keys + credentials in production
- **[CREDENTIALS_AUDIT.md](CREDENTIALS_AUDIT.md)** — Rotation checklist & security audit
- **[.env.example](.env.example)** — Full inventory of all 40+ environment variables

Never commit `.env` to git; always use a secret manager (AWS Secrets Manager, Vault, etc.) in production.
