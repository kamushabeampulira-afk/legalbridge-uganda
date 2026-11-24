# LegalBridge Informal — Complete Setup Guide

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | Use pyenv or official installer |
| Node.js | 18+ | Use nvm recommended |
| PostgreSQL | 15+ | Local or Docker |
| Expo CLI | Latest | `npm install -g expo-cli` |
| Tesseract OCR | 5.x | For document OCR |
| ngrok | Latest | For USSD webhook tunnelling |

---

## Step 1 — Clone and configure

```bash
git clone <repository-url> legalbridge-informal
cd legalbridge-informal
cp .env.example .env
# Open .env and fill in your credentials
```

---

## Step 2 — PostgreSQL database

```sql
-- Run as postgres superuser
CREATE USER legalbridge_user WITH PASSWORD 'changeme';
CREATE DATABASE legalbridge_db OWNER legalbridge_user;
GRANT ALL PRIVILEGES ON DATABASE legalbridge_db TO legalbridge_user;
```

Update `.env`:
```
DB_NAME=legalbridge_db
DB_USER=legalbridge_user
DB_PASSWORD=changeme
DB_HOST=localhost
DB_PORT=5432
```

---

## Step 3 — Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (for admin panel)
python manage.py createsuperuser

# Seed sample legal data
python manage.py seed_legal_data

# Seed and index into ChromaDB (requires OpenAI key)
python manage.py seed_legal_data --index

# Start development server
python manage.py runserver
```

Backend runs at: http://127.0.0.1:8000
Admin panel: http://127.0.0.1:8000/admin/

---

## Step 4 — Tesseract OCR installation

### Windows
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default path
3. Add to PATH: `C:\Program Files\Tesseract-OCR`
4. Verify: `tesseract --version`

### macOS
```bash
brew install tesseract
```

### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

---

## Step 5 — Mobile app setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo development server
npx expo start

# Press 'a' for Android emulator
# Press 'i' for iOS simulator
# Scan QR code with Expo Go app on your device
```

**Important**: Update the API base URL for device testing.
In `mobile/services/api.ts`, change `127.0.0.1` to your machine's LAN IP:
```typescript
const BASE_URL = __DEV__
  ? 'http://192.168.1.XXX:8000/api'   // Your LAN IP
  : 'https://api.legalbridgeug.org/api';
```

---

## Step 6 — USSD setup (Africa's Talking)

### 1. Create AT sandbox account
- Register at: https://account.africastalking.com/auth/register
- Create a sandbox app

### 2. Get credentials
Add to `.env`:
```
AT_USERNAME=sandbox
AT_API_KEY=your-sandbox-api-key
AT_ENVIRONMENT=sandbox
```

### 3. Expose backend with ngrok
```bash
# In a new terminal
ngrok http 8000
# Note the https URL: https://xxxx.ngrok.io
```

### 4. Configure AT webhook
- Go to AT sandbox → USSD → Create channel
- Shortcode: `*384*0#`
- Callback URL: `https://xxxx.ngrok.io/api/ussd/webhook/`

### 5. Test with AT simulator
- Open: https://simulator.africastalking.com/
- Shortcode: `*384*0#`
- Phone: `+256700000001`

---

## Step 7 — API keys

### OpenAI
1. Get key: https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

### ElevenLabs (optional TTS)
1. Get key: https://elevenlabs.io
2. Find voice IDs in your ElevenLabs dashboard
3. Add to `.env`: `ELEVENLABS_API_KEY=...`

---

## Step 8 — Add verified legal sources

1. Obtain verified legal documents from:
   - Uganda Legal Information Institute: https://ulii.org
   - Uganda Parliament website: https://parliament.go.ug
   - Uganda Gazette

2. Upload via Django admin:
   - Go to http://127.0.0.1:8000/admin/
   - Navigate to Legal Data → Legal Sources
   - Add source with full text
   - Use admin action "Approve and index"

3. Only approved + indexed sources are used in AI responses.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Common Issues

### "Tesseract not found"
Ensure Tesseract is in your system PATH. On Windows, add:
`C:\Program Files\Tesseract-OCR` to Environment Variables → PATH.

### "ChromaDB import error"
```bash
pip install chromadb --upgrade
```

### "CORS error from mobile app"
Add your Expo dev server URL to `CORS_ALLOWED_ORIGINS` in `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:8081,http://localhost:19006,http://192.168.1.XXX:8081
```

### "JWT token expired"
The app auto-refreshes tokens. If logged out unexpectedly, check
`JWT_REFRESH_TOKEN_LIFETIME_DAYS` in `.env`.

### "No legal sources found" / Uncertainty message
Run: `python manage.py seed_legal_data --index`
This indexes the sample legal sources into ChromaDB.

### USSD "Service unavailable"
- Verify ngrok is running and tunnel is active
- Check AT webhook URL matches ngrok URL
- Ensure Django server is running
- Check Django logs for errors

---

## Production Deployment Notes

1. Set `DJANGO_DEBUG=False`
2. Set strong `DJANGO_SECRET_KEY`
3. Configure PostgreSQL with proper credentials
4. Set up Redis for USSD session caching (replace LocMemCache)
5. Configure S3-compatible storage for media files
6. Set `AT_ENVIRONMENT=production` for live USSD
7. Use gunicorn + nginx
8. Enable HTTPS
9. Set `DJANGO_ALLOWED_HOSTS` to your domain
