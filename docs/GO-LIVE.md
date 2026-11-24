# LegalBridge — hosting checklist

Everything in the repository is done and merged to `main`. These are the only
steps that require your accounts, keys, and confirmation.

## 1. Keys to create first

| # | Tap / open | What to copy |
|---|------------|--------------|
| 1 | <https://aistudio.google.com/apikey> | Gemini API key — paste into `OPENAI_API_KEY` |
| 2 | <https://ai.google.dev/gemini-api/docs/models> | A current Gemini **Flash** model name — paste into `OPENAI_MODEL` |
| 3 | <https://api.sunbird.ai/register> then <https://api.sunbird.ai/keys> | Sunbird token — paste into `SUNBIRD_API_TOKEN` |
| 4 | <https://account.africastalking.com/> | Sandbox username + API key — paste into `AT_USERNAME` and `AT_API_KEY` |

> Rotate the OpenAI key that was previously pasted into chat. Do not paste any
> real key into Git, `render.yaml`, or `render.free.yaml`.

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
   | `OPENAI_API_KEY` | Gemini API key from step 1 |
   | `OPENAI_MODEL` | Current Gemini Flash model from step 2 |
   | `SUNBIRD_API_TOKEN` | Sunbird token from step 3 |
   | `AT_USERNAME` | `sandbox` |
   | `AT_API_KEY` | Africa's Talking sandbox key |

10. Wait for the first deploy. Startup runs migrations, seeding and ChromaDB
    indexing automatically.

## 3. Verify the API

Render gives you a URL like `https://legalbridge-demo.onrender.com`.

| Tap / open | Expected |
|------------|----------|
| `https://<your-host>/healthz` | Plain text `ok` |
| `https://<your-host>/admin/` | Django admin login page |
| `POST https://<your-host>/api/auth/token/` with a test user | JWT access token |

If `/healthz` shows `db unavailable`, check the Render logs and the Postgres
connection in the service **Environment** tab.

## 4. Point the mobile app at the API

Create `mobile/.env` locally (do **not** commit it):

```env
EXPO_PUBLIC_API_URL=https://<your-host>/api
```

Then rebuild/run Expo. Verify in the app:

- Login with a demo account.
- Open **Know My Rights** as a rider and as a vendor.
- Switch language between **English** and **Luganda**.
- Record a fresh demo voice note (not compressed WhatsApp audio).

## 5. Point USSD at the API

In the Africa's Talking dashboard, set the callback URL to:

```text
https://<your-host>/api/ussd/webhook/
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
