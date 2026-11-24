# LegalBridge — hosting checklist

Everything in the repository is done and merged to `main`. These are the only
steps that require your accounts, keys, and confirmation.

## Current demo (live)

- **App for presentation:** <https://legalbridge-app-free.onrender.com>
- API: <https://legalbridge-api-free.onrender.com>
- Health check: <https://legalbridge-api-free.onrender.com/healthz> → `ok`
- Blueprint: `legalbridge-demo` using `render.free.yaml` (commit `563f2fb`)
- `mobile/.env` is already set locally to the API URL above and is gitignored.

The presentation link is a real Expo web export of the app. Browser limitations
apply: USSD uses a `tel:` link and voice uses the browser speech fallback, so
use the phone/Expo build for the full native recording and USSD demo.

## 1. Keys to create first

| # | Tap / open | What to copy |
|---|------------|--------------|
| 1 | <https://console.groq.com/keys> | Groq API key — paste into `OPENAI_API_KEY` |
| 2 | <https://console.groq.com/docs/models> | Model ID is already set in the Blueprint (`openai/gpt-oss-20b`); no paste needed |
| 3 | <https://api.sunbird.ai/register> then <https://api.sunbird.ai/keys> | Sunbird token — paste into `SUNBIRD_API_TOKEN` |
| 4 | <https://account.africastalking.com/> | Sandbox username + API key — paste into `AT_USERNAME` and `AT_API_KEY` |

> Rotate the Groq, Sunbird, and OpenAI keys that were previously pasted into
> chat. Do not paste any real key into Git, `render.yaml`, or `render.free.yaml`.

## 2. Create the free Render deployment

1. Open <https://dashboard.render.com>.
2. Tap **New** → **Blueprint**.
3. Connect GitHub repo:
   `https://github.com/kamushabeampulira-afk/legalbridge-uganda`
4. Branch: **main**.
5. Blueprint file: **`render.free.yaml`**.
6. Blueprint name: `legalbridge-demo` (or any name you like).
7. Region: **Frankfurt** (already set in the file; keep it).
8. Tap **Apply**.
9. Fill the prompted values:

   | Prompt | Value |
   |--------|-------|
   | `OPENAI_API_KEY` | Groq API key from step 1 |
   | `OPENAI_MODEL` | Filled automatically by the Blueprint; leave it as-is |
   | `SUNBIRD_API_TOKEN` | Sunbird token from step 3 |
   | `AT_USERNAME` | `sandbox` |
   | `AT_API_KEY` | Africa's Talking sandbox key |

10. Wait for the first deploy. Startup runs migrations, seeding and ChromaDB
    indexing automatically.

## 3. Verify the API

The deployed host is `https://legalbridge-api-free.onrender.com`.

| Tap / open | Expected |
|------------|----------|
| `https://legalbridge-api-free.onrender.com/healthz` | Plain text `ok` |
| `https://legalbridge-api-free.onrender.com/admin/` | Django admin login page |
| `POST https://legalbridge-api-free.onrender.com/api/auth/token/` with a test user | JWT access token |

If `/healthz` shows `db unavailable`, check the Render logs and the Postgres
connection in the service **Environment** tab.

## 4. Point the mobile app at the API

Create `mobile/.env` locally (do **not** commit it):

```env
EXPO_PUBLIC_API_URL=https://legalbridge-api-free.onrender.com/api
```

Then rebuild/run Expo. The hosted database starts empty, so register a fresh
demo account in the app; the local test accounts were not copied. Verify:

- Register/login with that demo account.
- Open **Know My Rights** as a rider and as a vendor.
- Switch language between **English** and **Luganda**.
- Record a fresh demo voice note (not compressed WhatsApp audio).

## 5. Point USSD at the API

In the Africa's Talking dashboard, set the callback URL to:

```text
https://legalbridge-api-free.onrender.com/api/ussd/webhook/
```

Verify in the Africa's Talking simulator:

- Dial `*384*0#`.
- Select rider and vendor paths.
- Check rights menus match the app wording.

## 6. Remember the free-tier catch

- The free service sleeps after 15 idle minutes; the first tap after that takes
  about a minute.
- The free Postgres database expires **30 days** after creation. Put a reminder
  in your calendar to upgrade or back up before then.
- Uploads and vector data reset on restart; this is fine for judging, not for
  real user data.

## 7. When you need production

Create a second Blueprint from **`render.yaml`** instead. It uses paid plans,
keeps media and ChromaDB on a persistent disk, runs migrations before deploy,
and does not sleep.
