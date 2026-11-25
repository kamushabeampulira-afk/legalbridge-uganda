# Deploying LegalBridge to Render

This guide deploys the Django backend only. The Expo mobile app stays a local
project and points at the deployed API with `EXPO_PUBLIC_API_URL`.

`render.yaml` creates:

| Resource | Purpose |
|----------|---------|
| `legalbridge-api` | Docker web service (Gunicorn + Django) |
| `legalbridge-db` | Private PostgreSQL 15 database |
| `legalbridge-cache` | Private Redis-compatible Key Value instance |
| `legalbridge-app-data` | 10 GB persistent disk mounted at `/app/data` |

Docker is used instead of Render's native Python runtime because the OCR/PDF
pipeline needs `tesseract-ocr`, `poppler-utils` and `libgl`, which are installed
in `backend/Dockerfile`.

> **Before deploying:** rotate the OpenAI key that was previously pasted into
> chat. Do not put any API key in `render.yaml`, `render.free.yaml`,
> `mobile/.env`, or Git.

## Free demo deployment

`render.free.yaml` is a second Blueprint for a **zero-cost demo**. Use it for
judging and walkthroughs, not real users. It creates only free resources:

| Resource | Free behaviour |
|----------|----------------|
| `legalbridge-api-free` | Docker web service, 0.1 CPU / 512 MB, sleeps after 15 idle minutes (~1 min wake-up) |
| `legalbridge-db-free` | Free Postgres, 1 GB, **expires 30 days** after creation |
| `legalbridge-cache-free` | Free Key Value, 25 MB, no persistence |

Limitations to accept for a free demo:

- No persistent disk: uploads in `/app/media` and ChromaDB data in
  `/app/chroma_db` disappear on sleep, restart or redeploy.
- No Shell access. Seeding and indexing run automatically at boot via
  `seed_legal_data --if-empty` and `ensure_legal_index`.
- Free Key Value is memory-only, so USSD sessions are lost on restart.
- Free web services cannot attach disks or run one-off jobs, and Render may
  restart them at any time.
- One free Postgres per workspace. Upgrade it before the 30-day expiry if you
  want to keep the data.

To deploy the free demo:

1. Create a **Blueprint** and select `render.free.yaml` when prompted for the
   Blueprint file (or rename it to `render.yaml` in a separate branch).
2. Fill the prompted secrets:

   | Prompted key | Suggested free value |
   |--------------|----------------------|
   | `OPENAI_API_KEY` | Groq API key from <https://console.groq.com/keys> |
   | `OPENAI_MODEL` | Set in the Blueprint to `openai/gpt-oss-20b` (official Groq model ID) |
   | `SUNBIRD_API_TOKEN` | Free Sunbird token from <https://api.sunbird.ai/register> |
   | `AT_USERNAME` / `AT_API_KEY` | Sandbox Africa's Talking credentials |

3. Wait for the first boot. It runs migrations, `collectstatic`, seeds verified
   extracts once, rebuilds the ChromaDB index if empty, then starts Gunicorn.
4. Verify `https://<your-free-host>/healthz` returns `ok`.

The free Blueprint uses Groq's OpenAI-compatible endpoint for chat and English
speech, and Sunbird for Luganda speech, so it does not need a paid OpenAI or
ElevenLabs account. Actual model availability is still controlled by those
providers; see <https://console.groq.com/docs/models> for the current model list.

### Speed on the free plan

Measured response times:

| Step | Time |
|------|------|
| Speech to text, English (Groq Whisper) | about 3 s |
| Speech to text, Luganda (Sunbird) | about 35 s |
| Reading an answer aloud, English (Groq) | 7-9 s |
| Reading an answer aloud, Luganda (Sunbird) | about 25 s |
| Waking a sleeping service, then loading the legal search model | 1-2 min |

`SUNBIRD_VOICE_LANGUAGES=lg` sends only Luganda to Sunbird; everything else
uses Groq. `WARM_UP_ON_START=true` loads the search model while the server
starts, not during the first question. Large photos are shrunk to
`OCR_MAX_IMAGE_SIDE` pixels (default 2500) before OCR.

The biggest remaining delay is the free service sleeping after 15 idle minutes.
A free uptime monitor (for example UptimeRobot or cron-job.org) that requests
`https://<your-free-host>/healthz` every 10 minutes keeps it awake. One service
running all month uses about 744 of the workspace's 750 free instance hours, so
this only works if it is the only free web service in the workspace. The 0.1 CPU
also slows OCR and the first search; the Starter plan (0.5 CPU) is the paid fix.

## 1. Prepare the repository

1. Merge the deployment branch into `main` (or deploy directly from the branch
   that contains this `render.yaml`).
2. Push it to GitHub. Render will prompt for secrets during Blueprint creation.

No `.env` file is needed on Render. All configuration comes from the Blueprint
and the Render Dashboard.

## 2. Create the Blueprint

1. Go to <https://dashboard.render.com> → **New** → **Blueprint**.
2. Connect the `legalbridge-uganda` GitHub repository.
3. Select the branch containing `render.yaml`.
4. Name the Blueprint (for example `legalbridge`) and choose the same region as
   the resources already declared (`frankfurt`).
5. On **Apply**, fill the prompted secret values:

   | Prompted key | What to use |
   |--------------|-------------|
   | `OPENAI_API_KEY` | The **rotated** OpenAI key |
   | `ELEVENLABS_API_KEY` | Your ElevenLabs key, or leave blank if not using TTS |
   | `AT_USERNAME` | `sandbox` for testing, `production` for live USSD |
   | `AT_API_KEY` | Africa's Talking API key |

   `DJANGO_SECRET_KEY` is generated by Render. Database credentials and
   `REDIS_URL` are wired automatically from the created resources.

6. Wait for the first deploy. Render runs `migrate` and `collectstatic` before
   starting Gunicorn, then seeds verified extracts and referrals once.

## 3. Verify the deployment

Find the service URL on the Render dashboard (for example
`https://legalbridge-api.onrender.com`).

```bash
curl https://legalbridge-api.onrender.com/healthz
# expected: ok
```

Also check:

- `/admin/` loads the Django admin login page.
- `POST /api/auth/token/` returns a JWT for a test user.
- Render logs show no `DisallowedHost`, `SECURE_SSL_REDIRECT` loop, or missing
  static file errors.

`settings_production.py` automatically adds Render's `RENDER_EXTERNAL_HOSTNAME`
to `ALLOWED_HOSTS`. If you add a custom domain, also update these Blueprint env
vars (or edit them in the Dashboard):

- `DJANGO_ALLOWED_HOSTS` — e.g. `legalbridgeug.org,api.legalbridgeug.org`
- `CORS_ALLOWED_ORIGINS` — your public web/expo origin(s)
- `DJANGO_CSRF_TRUSTED_ORIGINS` — the HTTPS origin used for admin forms

## 4. Seed or re-index legal data (one-off)

The first deploy seeds verified legal extracts and referrals. To enable RAG
answers, index them into ChromaDB from **Render Shell** (web service → Shell):

```bash
python manage.py seed_legal_data --index
```

If sources are already seeded and only the vector index is missing (for example
after replacing the disk), rebuild it without re-seeding:

```bash
python manage.py ensure_legal_index
```

`seed_legal_data --index` re-seeds every source and updates `last_verified_at`;
review the source PDFs in `legal_sources/official/` before relying on indexed
answers.

Do **not** use `AI_DEMO_MODE=True` in production. Missing keys should surface as
errors, not placeholder explanations.

## 5. Point the mobile app at the API

Create `mobile/.env` locally (do not commit it):

```env
EXPO_PUBLIC_API_URL=https://legalbridge-api.onrender.com/api
```

`mobile/services/api.ts` now reads `EXPO_PUBLIC_API_URL`, falling back to
`http://localhost:8000/api` in development and `https://api.legalbridgeug.org/api`
otherwise. Rebuild the Expo app after changing the value.

For web builds, add the Expo dev server origin to `CORS_ALLOWED_ORIGINS` on
Render. Native apps do not enforce CORS.

## 6. Configure Africa's Talking USSD

In the Africa's Talking dashboard, set the callback URL to:

```text
https://legalbridge-api.onrender.com/api/ussd/webhook/
```

Use `AT_ENVIRONMENT=sandbox` while testing, then switch to `production` and use
the live shortcode before launch. The USSD menus are in all five app languages.
Runyankore, Acholi and Lugbara are drafts that need native-speaker review.

## 7. Storage notes

- Uploaded documents are written to `/app/data/media` on the persistent disk.
  This is fine for a single-instance demo, but the disk does not scale across
  instances. For launch, move media to S3-compatible storage using
  `django-storages` (already in `requirements.txt`).
- ChromaDB persists at `/app/data/chroma_db`. If the disk is replaced, re-run
  `python manage.py seed_legal_data --index`.
- A persistent disk prevents scaling the web service to multiple instances.
  Keep `numInstances` at 1 until media/vector storage is externalized.

## 8. Cost and cleanup

Paid plans are used because the OCR dependencies and persistent disk need more
than the free tier, and `preDeployCommand`/`initialDeployHook` require a paid
web service. Check Render pricing before applying. To remove everything, delete
the Blueprint resources in the Render Dashboard; no cloud credentials are stored
in this repository.
