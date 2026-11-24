# LegalBridge Informal — System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌─────────────────────┐      ┌──────────────────────────────┐  │
│  │  React Native App   │      │   USSD (Any phone, no data)  │  │
│  │  (Expo / TypeScript)│      │   Africa's Talking Gateway   │  │
│  └──────────┬──────────┘      └──────────────┬───────────────┘  │
└─────────────┼────────────────────────────────┼──────────────────┘
              │ HTTPS REST API                  │ POST webhook
              ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND LAYER                              │
│                   Django + DRF (Python)                          │
│                                                                  │
│  ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────────┐ │
│  │  users   │ │ documents │ │ legal_data│ │   channels_app   │ │
│  │          │ │  + OCR    │ │   + RAG   │ │  (USSD webhook)  │ │
│  └──────────┘ └───────────┘ └─────┬─────┘ └──────────────────┘ │
│  ┌──────────┐ ┌───────────┐       │        ┌──────────────────┐ │
│  │  voice   │ │referrals  │       │        │  subscriptions   │ │
│  │ STT/TTS  │ │ directory │       │        │  + analytics     │ │
│  └──────────┘ └───────────┘       │        └──────────────────┘ │
└──────────────────────────────────┼─────────────────────────────┘
                                   │
              ┌────────────────────┼──────────────────────┐
              │                    │                       │
              ▼                    ▼                       ▼
┌─────────────────┐  ┌─────────────────────┐  ┌──────────────────┐
│   PostgreSQL    │  │  ChromaDB (Vector)  │  │   OpenAI API     │
│   (Primary DB)  │  │  (Legal RAG index)  │  │  GPT-4o + Whisper│
│                 │  │                     │  │  + TTS           │
└─────────────────┘  └─────────────────────┘  └──────────────────┘
```

## Component Descriptions

### Mobile App (React Native + Expo)
- **Framework**: Expo SDK 51, Expo Router (file-based routing)
- **State**: Zustand (lightweight, no boilerplate)
- **HTTP**: Axios with JWT interceptor + auto-refresh
- **Storage**: expo-secure-store (tokens), AsyncStorage (preferences)
- **Audio**: expo-av (recording + playback)
- **Camera/Files**: expo-camera, expo-image-picker, expo-document-picker

### Backend (Django 5 + DRF)
- **Auth**: JWT via djangorestframework-simplejwt
- **Database**: PostgreSQL 15 via psycopg2
- **File storage**: Local media/ (dev), S3-compatible (production)
- **Rate limiting**: DRF throttles (20/min anon, 60/min user)
- **CORS**: django-cors-headers

### RAG Pipeline (ai_engine + legal_data)
1. User submits document or question
2. OCR extracts text (Tesseract / PyMuPDF)
3. Document classified by keyword heuristics
4. ChromaDB queried for relevant legal chunks (cosine similarity)
5. Retrieved chunks + user context passed to OpenAI GPT-4o
6. Response structured into labelled sections
7. Sources cited; uncertainty flag raised if no source found

### USSD (channels_app)
- Africa's Talking webhook: `POST /api/ussd/webhook/`
- Session state: Django cache (configure Redis for production)
- Menu tree: `ussd_menus.py` — CON/END format
- Menus: English, Luganda, Runyankore, Acholi, Lugbara (`LANGUAGE_OPTIONS` 1-5); untranslated menus fall back to English
- Shares same backend services as mobile app

### Voice (voice app)
- **STT**: OpenAI Whisper (`whisper-1`) — reliable in English only; local languages return an accuracy warning
- **TTS**: OpenAI TTS (`tts-1`) or ElevenLabs (configurable via env)
- Modular provider pattern — swap provider without app changes
- Local-language STT fallback: manual typed confirmation

## Data Flow: Document Analysis

```
User uploads image/PDF
        │
        ▼
documents/views.py → validate file type/size
        │
        ▼
documents/ocr.py → Tesseract OCR / PyMuPDF extraction
        │
        ▼
classify_document_type() → heuristic keyword classifier
        │
        ▼
ai_engine/engine.py → retrieve_relevant_chunks() [ChromaDB]
        │
        ├── No chunks found → UNCERTAINTY_RESPONSE (no hallucination)
        │
        └── Chunks found → OpenAI GPT-4o with strict prompt
                │
                ▼
        _parse_response_sections() → structured sections
                │
                ▼
        DocumentAnalysis saved → returned to mobile app
```

## Security Design

| Concern | Approach |
|---|---|
| Auth | JWT Bearer tokens, auto-refresh, secure storage |
| Secrets | Environment variables only, never in code |
| File uploads | Type + size validation before saving |
| User documents | Soft-delete, user-controlled deletion |
| Admin access | Superuser-only for sensitive query data |
| Rate limiting | DRF throttles on all endpoints |
| CORS | Explicit origin whitelist |
| Data minimisation | Phone number auth only; name optional |
| Consent | Explicit consent gate at registration |
| AI outputs | Strict prompts; uncertainty flag; no hallucination |
| Legal sources | Manual admin approval before RAG indexing |

## Database Schema Summary

```
lb_users              — Custom user model (phone auth)
lb_organisations      — Orgs (SACCOs, NGOs, associations)
lb_org_members        — Org membership links
lb_documents          — Uploaded documents + OCR results
lb_document_analyses  — AI-generated explanations
lb_legal_sources      — Verified Ugandan legal documents
lb_legal_provisions   — Individual sections/provisions
lb_legal_queries      — User question log (anonymised)
lb_ussd_sessions      — USSD session log
lb_legal_aid_orgs     — Legal aid directory
lb_legal_professionals— Legal professional directory
lb_subscription_plans — Configurable plans (UGX)
lb_org_subscriptions  — Active subscriptions
lb_sponsored_access   — Sponsored community access
lb_daily_usage_stats  — Aggregate analytics (no PII)
lb_doc_type_stats     — Document type aggregate stats
```
