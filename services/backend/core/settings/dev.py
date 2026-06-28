"""Local development settings."""

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# CORS: allow the local frontend dev servers (Next.js :3000, Vite :5173) out of
# the box so a browser frontend can call the API without extra config. Prod
# reads origins from CORS_ALLOWED_ORIGINS in the environment instead.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Database: inherits the SQLite default from base.py — local development uses a
# db.sqlite3 file in the project root, no server required. Export DATABASE_URL
# if you ever want to point local dev at Postgres instead.

# Convenience: the browsable API for poking at endpoints during development.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
