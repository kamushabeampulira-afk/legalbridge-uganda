# LegalBridge Informal
## ⚖️ Justice Within Reach

**LegalBridge Informal** is a voice-first, multi-channel legal first-aid platform for Uganda's informal workers — boda boda riders and market vendors. Built for **Hack4Justice 2026**.

---

## What It Does

| User need | LegalBridge solution |
|-----------|---------------------|
| Received a traffic notice and don't understand it | Upload photo → OCR → AI explanation citing verified Ugandan law |
| Stopped by a traffic officer | Guided questions → structured rights information |
| Received an eviction notice | Upload document or guided questions → explanation + next steps |
| Cannot afford a lawyer | In-app legal aid directory + USSD for no-internet access |
| Speaks Luganda, not comfortable typing | Voice recording → transcription → spoken AI answer |
| Has a feature phone, no internet | Dial `*384*0#` → USSD menu in English or Luganda |

---

## Project Structure

```
legalbridge-informal/
├── backend/              Django + DRF + PostgreSQL API
│   ├── config/           Settings, URLs, WSGI/ASGI
│   ├── users/            Custom phone-auth user model, organisations
│   ├── documents/        Upload, OCR (Tesseract/PyMuPDF), classification
│   ├── legal_data/       Verified legal sources, ChromaDB RAG, LegalQuery log
│   ├── ai_engine/        RAG pipeline, OpenAI GPT-4o, guided scenarios
│   ├── voice/            STT (Whisper) + TTS (OpenAI/ElevenLabs)
│   ├── channels_app/     USSD webhook (Africa's Talking)
│   ├── referrals/        Legal aid directory
│   ├── subscriptions/    Organisation plans (UGX, admin-configurable)
│   ├── analytics/        Anonymised aggregate stats
│   └── tests/            pytest test suite
│
├── mobile/               React Native + Expo (TypeScript)
│   ├── app/              Expo Router screens
│   │   ├── (auth)/       Login, Register
│   │   ├── (tabs)/       Home, Boda, Vendor, History, Profile
│   │   ├── document/     Upload + AI explanation
│   │   ├── boda/         "Stopped by officer" guided scenario
│   │   ├── vendor/       "Eviction" guided scenario
│   │   ├── ask.tsx       Free-text legal question
│   │   ├── voice.tsx     Voice recording + spoken answer
│   │   └── legal-help.tsx Legal aid directory
│   ├── components/ui/    Button, Card, SectionCard, DisclaimerBanner, etc.
│   ├── constants/        Colors, Typography, Spacing (design system)
│   ├── hooks/            useLanguage, useDocumentAnalysis, useAudioPlayer
│   ├── i18n/             English + Luganda translations
│   ├── services/api.ts   All backend API calls (Axios + JWT)
│   └── store/            Zustand global state (auth, language, user)
│
├── ussd/                 USSD docs + reference handler
├── legal_sources/        Verified legal documents + sample demo docs
├── docs/                 Architecture, API, Setup, Demo guides
├── scripts/              Setup and test scripts (Windows + Unix)
├── docker-compose.yml    One-command Docker startup
├── .env.example          All required environment variables
└── README.md
```

---

## Quick Start (5 minutes)

### Option A — Docker (easiest)

```bash
# 1. Clone and configure
git clone <repo-url> legalbridge-informal
cd legalbridge-informal
cp .env.example backend/.env
# Edit backend/.env — add OPENAI_API_KEY at minimum

# 2. Start everything
docker-compose up --build

# 3. Create admin user
docker-compose exec backend python manage.py createsuperuser
```

Backend: http://localhost:8000  
Admin: http://localhost:8000/admin/

### Option B — Manual (Windows)

```bat
# Backend
scripts\setup_backend.bat

# In a second terminal
cd backend
venv\Scripts\activate
python manage.py createsuperuser
python manage.py runserver

# Mobile (third terminal)
scripts\setup_mobile.bat
cd mobile
npx expo start
```

---

## Environment Variables

Copy `.env.example` to `backend/.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | ✅ | Long random string |
| `DB_NAME/USER/PASSWORD` | ✅ | PostgreSQL credentials |
| `OPENAI_API_KEY` | ✅ | GPT-4o + Whisper + TTS |
| `AT_USERNAME` / `AT_API_KEY` | For USSD | Africa's Talking |
| `ELEVENLABS_API_KEY` | Optional | Better TTS quality |

---

## Running Tests

```bash
cd backend
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux
pytest tests/ -v
```

Test coverage includes:
- User registration and authentication
- Document upload validation
- OCR text extraction and classification
- USSD session navigation (all menu paths)
- AI engine — anti-hallucination safeguard (uncertainty flag)
- Legal question API
- Referral directory filtering

---

## AI Safety Rules

LegalBridge enforces strict anti-hallucination rules in every AI prompt:

1. **Never invents** Ugandan laws, provisions, fines or procedures
2. **Only cites** sources retrieved from the verified ChromaDB index
3. **Raises uncertainty flag** if no verified source is found — displays: *"I cannot verify the applicable legal provision..."*
4. **Distinguishes** allegations from established facts
5. **Never declares** an eviction legal or illegal without full context
6. **Always refers** complex matters to qualified legal professionals
7. **Disclaimer** appears on every explanation screen

---

## Demo Scenarios (Hack4Justice 2026)

See `docs/DEMO.md` for the full walkthrough.

**Demo 1 — Boda Boda Rider**  
Upload sample traffic notice → OCR → AI explanation citing Traffic & Road Safety Act → practical next steps

**Demo 2 — Market Vendor**  
Upload eviction notice → explanation citing Markets Act 2023 → guided scenario → legal aid referral

**Demo 3 — USSD**  
Africa's Talking simulator → `*384*0#` → English/Luganda menus → both user categories

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Phone number auth (not email) | Most informal workers have a phone, not email |
| RAG with ChromaDB | Prevents hallucination — AI only uses verified sources |
| USSD as a separate channel | Feature phones, no internet — same backend services |
| Luganda UI text; limited Luganda STT | Whisper has no `lg` code; transcript is editable and web answers use browser TTS — honest limitation |
| Soft-delete documents | Users control their data; audit trail preserved |
| Admin approval before RAG indexing | No unverified legal text reaches production AI |
| UGX currency, admin-configurable prices | No hardcoded business logic |

---

## Legal Disclaimer

LegalBridge Informal provides **legal information**, not **legal advice**.  
It does not replace a qualified legal professional.  
For serious legal matters, always consult a qualified lawyer.

---

## Built for Hack4Justice 2026 — Uganda

*Making the first step towards justice easier to take.*
