# LegalBridge Informal — API Reference

Base URL (development): `http://127.0.0.1:8000/api`

All authenticated endpoints require: `Authorization: Bearer <access_token>`

---

## Authentication

### POST /auth/token/
Obtain JWT token pair.
```json
// Request
{ "phone_number": "+256700000001", "password": "password123" }

// Response 200
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### POST /auth/token/refresh/
Refresh access token.
```json
// Request
{ "refresh": "eyJ..." }

// Response 200
{ "access": "eyJ..." }
```

---

## Users

### POST /users/register/
Register new user. No auth required.
```json
// Request
{
  "phone_number": "+256700000001",
  "password": "securepass",
  "password_confirm": "securepass",
  "full_name": "John Mukasa",
  "user_type": "boda_boda",
  "preferred_language": "en",
  "consented_to_processing": true
}

// Response 201
{ "message": "Account created successfully.", "user_id": "uuid", "phone_number": "+256700000001" }
```

### GET /users/profile/
Returns current user profile. Auth required.

### PATCH /users/profile/
Update profile fields (full_name, preferred_language).

### POST /users/language/
```json
{ "language": "lg" }
```

### DELETE /users/delete/
Soft-deletes the authenticated user's account.

---

## Documents

### POST /documents/upload/
Upload a document for OCR processing.
- Content-Type: `multipart/form-data`
- Fields: `file` (JPG/PNG/PDF, max 10MB), `user_category`, `language`

```json
// Response 201
{
  "id": "uuid",
  "status": "completed",
  "doc_type": "traffic_notice",
  "extracted_text": "...",
  "ocr_confidence": 0.87
}
```

### POST /documents/{id}/analyze/
Trigger AI analysis on an uploaded document.
```json
// Request
{ "language": "en" }

// Response 200
{
  "id": "uuid",
  "summary": "This appears to be a traffic violation notice...",
  "what_it_means": "...",
  "relevant_law": "...",
  "details_to_check": "...",
  "next_steps": ["Keep the notice", "Note the reference number", "..."],
  "missing_information": "...",
  "where_to_get_help": "...",
  "legal_sources_used": [{"title": "...", "source_url": "..."}],
  "has_verified_sources": true,
  "uncertainty_flag": false
}
```

### GET /documents/history/
Returns paginated list of user's documents.

### GET /documents/{id}/
Returns document with full analysis.

### DELETE /documents/{id}/delete/
User deletes their own document (soft delete + file removal).

---

## Legal

### POST /legal/ask/
Free-text legal question via RAG.
```json
// Request
{
  "question": "What documents must I carry when riding a boda boda?",
  "user_category": "boda_boda",
  "language": "en"
}

// Response 200
{
  "answer": "...",
  "legal_sources": [...],
  "has_verified_sources": true,
  "uncertainty_flag": false,
  "disclaimer": "This is legal information, not legal advice..."
}
```

### GET /legal/categories/?subject=traffic
Returns approved legal sources filtered by subject.
Subjects: `traffic`, `markets`, `employment`, `land`, `local_gov`, `general`

### GET /legal/sources/{id}/
Returns a specific legal source.

---

## AI Guided Scenarios

### POST /ai/boda-stopped/
```json
// Request
{
  "told_about": "Officer said I had no insurance",
  "has_written_notice": "no",
  "penalty_mentioned": "UGX 50,000",
  "has_reference": "not_sure",
  "additional_details": "",
  "language": "en"
}

// Response 200
{
  "guidance": "...",
  "legal_sources": [...],
  "has_verified_sources": true,
  "uncertainty_flag": false,
  "disclaimer": "..."
}
```

### POST /ai/eviction-guidance/
```json
// Request
{
  "has_allocation_slip": "yes",
  "has_receipts": "yes",
  "notice_issuer": "Market manager",
  "reason_given": "Market redevelopment",
  "deadline": "30 June 2024",
  "additional_details": "",
  "language": "en"
}
```

---

## Voice

### POST /voice/transcribe/
- Content-Type: `multipart/form-data`
- Fields: `audio` (MP3/WAV/M4A/WebM, max 25MB), `language`
```json
// Response 200
{
  "transcription": "What documents must I carry...",
  "warning": null,
  "language": "en"
}
```

### POST /voice/synthesize/
```json
// Request
{ "text": "This document is a traffic violation notice...", "language": "en" }

// Response 200
{ "audio_url": "https://.../media/audio/tts_uuid.mp3", "language": "en" }
```

---

## Referrals

### GET /referrals/legal-aid/?district=Kampala&is_free=true
Returns verified legal aid organisations.

### GET /referrals/professionals/?district=Kampala
Returns verified legal professionals.

---

## USSD

### POST /api/ussd/webhook/
Africa's Talking webhook. NOT called directly — AT gateway calls this.
- Content-Type: `application/x-www-form-urlencoded`
- Fields: `sessionId`, `serviceCode`, `phoneNumber`, `text`
- Response: plain text starting with `CON` or `END`

---

## Analytics (Admin only)

### GET /analytics/dashboard/
Returns aggregate usage statistics. Requires `is_staff=True`.

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error — check response body |
| 401 | Unauthenticated — missing or expired token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not found |
| 429 | Rate limit exceeded |
| 500 | Server error — check Django logs |
