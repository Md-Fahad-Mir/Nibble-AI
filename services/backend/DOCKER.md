# NibblAI Backend — Docker Deployment Guide

Production-grade containerization for the NibblAI Django backend. Every file
described here was generated from the actual codebase and validated by building
and running the full stack (migrations applied, health check green, non-root,
gunicorn serving, scheduler running).

---

## 1. Architecture Summary

| Concern | Finding |
|---|---|
| **Language / Runtime** | Python 3.13 (`.python-version`, `requires-python >=3.13`) |
| **Framework** | Django 6.0 + Django REST Framework, JWT auth (simplejwt), OpenAPI via drf-spectacular |
| **Package manager** | `uv` with a committed `uv.lock` (reproducible installs) |
| **App layout** | 16 local apps under `Apps/` (note the capital **A**), routed under `/api/v1/` |
| **Database** | PostgreSQL only (`psycopg[binary]`); `DATABASE_URL` or discrete `DB_*` vars |
| **Cache / Throttling** | DRF throttling backed by Django cache — LocMem in dev, **Redis in prod** |
| **Background work** | No Celery/RQ. Cron-style management commands (notifications, reservation/review expiry, held-review release, billing, analytics) |
| **Message queue** | None |
| **Static files** | `collectstatic` → `staticfiles/`, served by **WhiteNoise** in prod |
| **Media (uploads)** | Receipt images on local disk (`media/`); S3 is a planned swap |
| **Email** | SMTP (console backend in dev) |
| **External APIs** | Anthropic / OpenAI / Gemini / Firebase FCM — all optional, mock when unset |
| **WSGI/ASGI** | `core.wsgi:application` (default settings module = `core.settings.prod`) |
| **Health check** | `GET /api/v1/health/` — returns 200 + DB connectivity, 503 if DB down |
| **Settings** | Split: `core.settings.{base,dev,prod,test}` |

### Changes made to support production containers

These were missing for a real deployment and have been added:

1. **`gunicorn`** — there was no production WSGI server (only `runserver`).
2. **`whitenoise`** — nothing served static assets with `DEBUG=False` (admin +
   Swagger UI would have broken). Wired into prod middleware + `STORAGES`.
3. **`redis`** + prod cache wiring — `base.py` hardcoded LocMem despite a comment
   claiming Redis auto-detection. Under multiple gunicorn workers, per-process
   LocMem would multiply every throttle limit by the worker count. Prod now uses
   Redis when `REDIS_URL` is set.
4. **Proxy/Docker-friendly prod settings** — loopback kept in `ALLOWED_HOSTS`
   for in-container health checks, `SECURE_SSL_REDIRECT` made env-configurable,
   `/api/v1/health/` exempted from the HTTPS redirect, and
   `CSRF_TRUSTED_ORIGINS` / `SECURE_HSTS_SECONDS` made configurable.

Dependencies are tracked in `pyproject.toml` and pinned in `uv.lock`.

---

## 2. Files

| File | Purpose |
|---|---|
| `Dockerfile` | Multi-stage (`base` → `builder` → `dev` / `prod`), non-root, healthcheck |
| `entrypoint.sh` | Waits for DB/Redis, migrates, (optional) collectstatic, execs the process |
| `.dockerignore` | Keeps host `.venv`, secrets, caches, and media out of the build context |
| `docker-compose.dev.yml` | Hot-reload dev stack (Postgres + Redis + autoreloading Django) |
| `docker-compose.prod.yml` | Gunicorn + Postgres + Redis + scheduler, healthchecks, named volumes |
| `.env.example` | Documented template for every variable (copy to `.env`) |
| `docker-compose.yml` | Pre-existing "Postgres only" convenience file (left untouched) |

---

## 3. Quick Start

### Development (hot reload)

```bash
cd services/backend
cp .env.example .env        # optional; the dev stack has safe defaults
docker compose -f docker-compose.dev.yml up --build
```

- API: <http://localhost:8000/api/v1/>
- Swagger: <http://localhost:8000/api/docs/>
- Source is bind-mounted; edits reload automatically. The image's `/app/.venv`
  is preserved via an anonymous volume, so the host venv never shadows it.

Create an admin user / seed data:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
docker compose -f docker-compose.dev.yml exec backend python manage.py seed_nibblai --users 10 --brands 5
```

### Production

```bash
cd services/backend

# Provide secrets via your shell / secret manager (NOT a committed .env):
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export ALLOWED_HOSTS="api.nibblai.app"
export CSRF_TRUSTED_ORIGINS="https://api.nibblai.app"
export POSTGRES_PASSWORD="<strong-password>"
export EMAIL_HOST_USER="apikey"
export EMAIL_HOST_PASSWORD="<sendgrid/ses key>"

docker compose -f docker-compose.prod.yml up -d --build
```

Required variables are enforced with `${VAR:?…}` — the stack refuses to start if
`SECRET_KEY`, `ALLOWED_HOSTS`, or `POSTGRES_PASSWORD` are missing.

Put a TLS-terminating reverse proxy (nginx, Caddy, ALB, Cloudflare) in front of
the backend on port 8000 and forward `X-Forwarded-Proto: https`.

---

## 4. Operations

- **Migrations** run automatically on backend start (`RUN_MIGRATIONS=1`). The
  `scheduler` service is pinned to `RUN_MIGRATIONS=0` so only one service migrates.
- **Static files** are baked into the prod image at build time (WhiteNoise
  manifest). No volume or extra web server required.
- **Periodic jobs** run in the `scheduler` service on a fixed interval
  (`SCHEDULER_INTERVAL_SECONDS`, default 3600). For finer per-job schedules,
  replace it with system cron or Kubernetes CronJobs invoking the same image,
  e.g. `docker compose -f docker-compose.prod.yml run --rm backend \
  python manage.py send_notifications`.
- **Managed services**: to use RDS / Cloud SQL / ElastiCache, delete the `db`
  and `redis` services and set `DATABASE_URL` / `REDIS_URL` to the endpoints.
- **Scaling**: increase `GUNICORN_WORKERS` (rule of thumb `2 × CPU + 1`) or run
  multiple `backend` replicas behind the proxy. Redis keeps throttle counters
  consistent across all of them.

---

## 5. Security Notes

- Container runs as a non-root user (`app`, uid/gid 1000).
- No secrets are baked into the image; `.dockerignore` excludes `.env`, `*.pem`,
  `*.key`, and the host `.venv`. The build-time `SECRET_KEY` is a throwaway used
  only so `collectstatic` can import settings; it is never used at runtime.
- `python manage.py check --deploy --settings=core.settings.prod` passes with 0
  issues (HSTS, secure cookies, SSL redirect, content-type nosniff).
- `/api/v1/health/` is exempt from the HTTPS redirect so load-balancer probes
  over plain HTTP succeed; all other paths 301 to HTTPS.
- Postgres and Redis are not published to the host in prod (internal network
  only); only the backend port is exposed.
- Pin and scan the base image (`python:3.13-slim-bookworm`) regularly; rebuild
  to pick up OS CVE fixes.

---

## 6. Performance Notes

- Multi-stage build: the final image excludes `uv`, build caches, and dev cruft.
- Dependency layer is keyed on `pyproject.toml` + `uv.lock`, so application code
  edits do not re-resolve/re-download dependencies.
- `UV_COMPILE_BYTECODE=1` precompiles `.pyc` for faster cold starts.
- gunicorn uses `gthread` workers with `--max-requests` recycling to bound
  memory growth, and `--forwarded-allow-ips '*'` so proxy headers are honored.
- Redis-backed cache makes throttling correct and shared across workers.
- WhiteNoise serves pre-compressed, hashed static assets with far-future caching.

---

## 7. Zero-Downtime Considerations

- Healthchecks gate readiness; `depends_on: condition: service_healthy` ensures
  the backend only starts once Postgres and Redis are healthy.
- `restart: unless-stopped` recovers from crashes.
- gunicorn `--graceful-timeout` lets in-flight requests drain on restart.
- For true rolling deploys, run behind an orchestrator (ECS/Kubernetes/Swarm)
  or use `docker compose up -d --no-deps --build backend` with a proxy that
  only routes to healthy containers. Keep migrations backward-compatible
  (expand/contract) so old and new code can run against the same schema briefly.

---

## 8. Validation Checklist

Build & static:
- [x] `docker build --target prod` succeeds
- [x] `docker build --target dev` succeeds
- [x] `collectstatic` runs at build (157 files, 453 post-processed via WhiteNoise manifest)
- [x] Image runs as non-root (`uid=1000(app)`)

Runtime (prod stack):
- [x] Postgres & Redis come up healthy; backend waits for both
- [x] Migrations apply automatically on boot
- [x] gunicorn serves 3 workers on `0.0.0.0:8000`
- [x] `GET /api/v1/health/` → `{"status":"ok","database":"ok"}`
- [x] HTTPS redirect: `/api/v1/config/` → 301, `/api/v1/health/` exempt
- [x] `scheduler` runs all periodic management commands

Pre-deploy (run before shipping):
- [ ] `python manage.py check --deploy --settings=core.settings.prod` → 0 issues
- [ ] `python manage.py makemigrations --check --dry-run` → no changes
- [ ] Real `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` set
- [ ] Transactional email provider configured (not personal Gmail)
- [ ] TLS terminates at the proxy and forwards `X-Forwarded-Proto`
- [ ] Database backups + monitoring/error tracking wired up

---

## 9. Cleanup

```bash
# Dev
docker compose -f docker-compose.dev.yml down -v

# Prod (and any ephemeral test containers)
docker compose -f docker-compose.prod.yml down -v
docker rm -f nibblai_ssltest 2>/dev/null || true
```
