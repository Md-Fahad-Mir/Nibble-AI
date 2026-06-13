# Secrets Management Guide

This document describes how to safely manage secrets (API keys, credentials, passwords) for the NibblAI backend.

## The Rule: Never Commit Secrets

- **`.env` is gitignored** — never appears in git history ✓
- **`.env.example` contains placeholders only** — safe to commit
- **Production secrets go in a secret manager**, not env files

## Local Development

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in local values** (for development only):
   - `SECRET_KEY`: use the default `dev-insecure-change-me` (it's fine locally)
   - `DB_*`: match your Docker Postgres (default: `nibblai`/`nibblai`)
   - `DEBUG=True`: for local development
   - Email: use `django.core.mail.backends.console.EmailBackend` (prints to stdout)
   - AI keys: leave commented out (uses mocks)

3. **Run the app:**
   ```bash
   docker compose up -d db
   python manage.py migrate
   python manage.py runserver
   ```

## Production Deployment

**Never use `.env` files in production.** Always inject secrets via your hosting platform's secret manager.

### Step 1: Generate a Strong `SECRET_KEY`

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Output: k3b9...xyz (copy this)
```

### Step 2: Choose a Secret Manager

Pick one based on your hosting platform:

| Platform | Secret Manager | Docs |
|----------|---|---|
| **AWS** | AWS Secrets Manager or Systems Manager Parameter Store | [link](https://docs.aws.amazon.com/secretsmanager/) |
| **Google Cloud** | Secret Manager | [link](https://cloud.google.com/secret-manager/docs) |
| **Azure** | Key Vault | [link](https://docs.microsoft.com/en-us/azure/key-vault/) |
| **Render** | Environment variables (encrypted at rest) | [link](https://render.com/docs/environment-variables) |
| **Railway** | Variables (encrypted) | [link](https://docs.railway.app/plugins/variables) |
| **Fly.io** | Secrets | [link](https://fly.io/docs/reference/secrets/) |
| **Heroku** | Config vars | [link](https://devcenter.heroku.com/articles/config-vars) |
| **Self-hosted** | HashiCorp Vault | [link](https://www.vaultproject.io/) |

### Step 3: Populate Required Secrets

At minimum, provide these via your secret manager:

```
SECRET_KEY                 = <strong-random-key-from-step-1>
ALLOWED_HOSTS              = api.nibblai.app,www.nibblai.app
DEBUG                      = False
DATABASE_URL               = postgres://user:pass@db.internal:5432/nibblai
EMAIL_HOST_USER            = mailer@nibblai.app
EMAIL_HOST_PASSWORD        = <SendGrid/SES API key, NOT personal Gmail>
```

### Step 4: Inject at Runtime

**Docker + Docker Compose:**
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
      DATABASE_URL: ${DATABASE_URL}
      EMAIL_HOST_USER: ${EMAIL_HOST_USER}
      EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD}
```

**Render / Railway / Fly.io / Heroku:**
- Use the platform's UI to set environment variables as **secrets**
- They are injected automatically at deploy time
- Never logged or visible in build logs

**Kubernetes:**
```yaml
# k8s-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: nibblai-secrets
type: Opaque
stringData:
  SECRET_KEY: ...
  DATABASE_URL: ...
  EMAIL_HOST_PASSWORD: ...
---
# deployment.yaml
spec:
  containers:
  - name: backend
    envFrom:
    - secretRef:
        name: nibblai-secrets
```

**HashiCorp Vault:**
```bash
vault kv put secret/nibblai \
  SECRET_KEY=... \
  DATABASE_URL=... \
  EMAIL_HOST_PASSWORD=...
```

Then in your app, read from Vault at startup (hvac SDK or Vault agent).

### Step 5: Run the Deployment Check

Before deploying, verify all required secrets are in place:

```bash
python manage.py check --deploy --settings=core.settings.prod
# Should output: System check identified no issues (0 silenced).
```

## Secret Rotation

### Rotating `SECRET_KEY`

**Invalidates all sessions and refresh tokens.** Plan for user re-login.

```bash
# 1. Generate a new key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 2. Update your secret manager
# 3. Redeploy the app
# 4. All existing JWTs will be invalid (users must log back in)
```

### Rotating API Keys (OpenAI, Anthropic, etc.)

For each provider:

```bash
# 1. Log in to the provider's console
# 2. Revoke the old key
# 3. Generate a new key
# 4. Update your secret manager
# 5. Redeploy (no user impact)
```

**Example: OpenAI**
- Go to https://platform.openai.com/account/api-keys
- Click the trash icon next to your old key
- Click "Create new secret key"
- Copy the new key
- Update `OPENAI_API_KEY` in your secret manager
- Redeploy

**Example: AWS Secrets Manager**
```bash
aws secretsmanager put-secret-value \
  --secret-id nibblai/OPENAI_API_KEY \
  --secret-string "sk-proj-new-key-here"
```

### Rotating Database Password

```bash
# 1. Change the password in your database (AWS RDS, Cloud SQL, etc.)
# 2. Update DATABASE_URL in your secret manager
# 3. Redeploy the app
```

## Monitoring & Audit

### What to Monitor

- **Suspicious API key usage** (many failed requests, unusual IPs/times)
- **Secret manager access logs** (who accessed what, when)
- **Failed deployments** (might indicate a secret mismatch)

### Audit Trail

**AWS Secrets Manager:**
```bash
aws secretsmanager list-secret-version-ids --secret-id nibblai/SECRET_KEY
```

**Vault:**
```bash
vault audit list
vault audit enable file file_path=/var/log/vault-audit.log
```

## Best Practices

1. **Principle of least privilege:**
   - Each secret gets a separate API key (don't share)
   - Scope keys to the minimum permissions (e.g., SendGrid marketing email only)
   - Restrict by IP/referrer where the provider allows

2. **Separate secrets by environment:**
   - `nibblai-prod-SECRET_KEY` (production)
   - `nibblai-staging-SECRET_KEY` (staging)
   - Don't reuse prod secrets in staging/dev

3. **Document the source:**
   ```
   # Credential inventory (store in a password manager, not git):
   SECRET_KEY       → generated by python -c "import secrets; ..."
   OPENAI_API_KEY   → platform.openai.com/account/api-keys
   EMAIL_HOST_PASSWORD → SendGrid API key (sendgrid.com/settings/api_keys)
   DB_PASSWORD      → AWS RDS console (rds.amazonaws.com)
   ```

4. **Use expiring keys where possible:**
   - Some providers support key expiry (e.g., AWS IAM keys)
   - Set auto-rotation schedules (annual minimum)

5. **Never use personal accounts in production:**
   - Gmail app-password ✗ (personal account, rate-limited)
   - SendGrid API key ✓ (scoped, business account)
   - Stripe business key ✓ (separable from personal account)

6. **Log access (but not the secrets):**
   - ✓ "User requested OPENAI_API_KEY at 2026-06-05T14:23:00Z"
   - ✗ "OPENAI_API_KEY=sk-proj-xxx" in logs

## Troubleshooting

### "settings.py: SECRET_KEY not found"
- Verify the secret is set in your secret manager
- Verify the key name matches exactly (case-sensitive)
- Check the app/container is picking up env vars (run `env | grep SECRET_KEY`)

### "ALLOWED_HOSTS invalid"
- Check that `ALLOWED_HOSTS` matches your domain (no trailing slash, comma-separated)
- Example: `api.nibblai.app,www.nibblai.app` ✓
- Example: `api.nibblai.app/` ✗

### "Database connection refused"
- Verify `DATABASE_URL` is correct (host, port, credentials)
- Verify the database server is running and accessible from the app
- Check network security groups (AWS SG, GCP firewall, etc.) allow the app's IP

### "Email not sending"
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are correct
- Check provider rate limits (Gmail limits ~100 emails/hour)
- Verify the `From` domain is authenticated with SPF/DKIM
- Check logs: `python manage.py shell` → `from django.core.mail import send_mail; send_mail(...)`

## References

- [Django security docs](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP: Secrets Management](https://owasp.org/www-community/attacks/Sensitive_Data_Exposure)
- [12-Factor App: Config](https://12factor.net/config)
