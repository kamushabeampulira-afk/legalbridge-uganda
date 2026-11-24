# LegalBridge Informal — Hack4Justice 2026 Demo Guide

## Demo Overview

Two complete user journeys + live USSD demonstration.
All documents are clearly labelled SAMPLE DATA.
All user information is fictional.

---

## Setup Checklist Before Demo

- [ ] Backend running: `python manage.py runserver`
- [ ] Sample data seeded: `python manage.py seed_legal_data --index`
- [ ] Mobile app running: `npx expo start`
- [ ] ngrok tunnel active (for USSD): `ngrok http 8000`
- [ ] AT simulator open: https://simulator.africastalking.com/
- [ ] AT webhook URL set to: `https://<ngrok-url>/api/ussd/webhook/`
- [ ] Demo documents ready (see `/legal_sources/sample_docs/`)
- [ ] OpenAI API key configured in `.env`

---

## Demo 1: Boda Boda Rider

**User**: John Mukasa, boda boda rider, Kampala

**Scenario**: John received a traffic violation notice and does not understand it.

### Steps

**1. Open the app**
- Splash screen → language selection (choose English)
- Log in as demo user or register quickly

**2. Navigate to Boda Boda**
- Home → Boda Boda Rider card
- Show the dashboard with four clear options

**3. Upload a document**
- Tap "Upload a Traffic Notice"
- Use sample document: `legal_sources/sample_docs/sample_traffic_notice.jpg`
- Take photo OR choose from files
- Preview → "Get Explanation"
- Show loading states: Uploading → Reading → Analysing

**4. View the explanation**
Show each section clearly:
- **What Your Document Says** — plain-language summary
- **What This May Mean** — implications without conclusions
- **Relevant Ugandan Law** — cites Traffic & Road Safety Act
- **Important Details to Check** — reference number, deadline
- **Missing Information** — what is absent from the notice
- **Recommended Next Steps** — numbered practical list
- **Where to Seek Help** — legal aid referrals

Point out:
- Audio playback button (listen to explanation)
- Legal source citation at bottom
- Disclaimer: "This is legal information, not legal advice"

**5. Guided scenario — stopped by officer**
- Navigate back → "I Was Stopped by an Officer"
- Fill in: "Officer said I had no insurance"
- Select: Written notice = No, Penalty mentioned = UGX 50,000
- Submit → show structured guidance
- Emphasise: allegation presented as allegation, not fact

**Key talking points**:
- No legal provisions were invented
- Sources are cited
- Uncertainty message shown if no source found
- User always directed to legal professionals for complex matters

---

## Demo 2: Market Vendor

**User**: Sarah Atim, market vendor, Nakasero Market

**Scenario**: Sarah received an eviction notice from market management.

### Steps

**1. Navigate to Market Vendor**
- Home → Market Vendor card

**2. Upload eviction notice**
- Tap "Upload a Document"
- Use sample: `legal_sources/sample_docs/sample_eviction_notice.jpg`
- Submit → view explanation

Show the system:
- Identifies document as "Eviction Notice"
- Explains what the notice says
- Retrieves Markets Act 2023 provisions
- Highlights: right to written notice, right to respond
- Lists missing information (no reason given, no reference number)
- Recommends: keep documents, seek legal aid, do not leave without written notice

**3. Guided eviction scenario**
- Navigate to "I Was Told to Leave My Stall"
- Answers: Has allocation slip = Yes, Has receipts = Yes
- Issuer = "Market manager", Reason = "Market redevelopment", Deadline = "2 weeks"
- Submit → structured guidance
- Show: legal provisions cited, next steps, referral to FIDA Uganda

**4. Find Legal Help**
- Navigate to Find Legal Help
- Show FIDA Uganda listing with phone and website
- Show Uganda Law Society listing

**Key talking points**:
- System never declares eviction legal or illegal
- Always uses "may" language
- Documents user's rights clearly
- Connects to real legal aid organisations

---

## Demo 3: USSD (feature phone / no internet)

**Setup**: Africa's Talking simulator at simulator.africastalking.com

### Steps

**1. Open AT simulator**
- Set shortcode: `*384*0#`
- Enter test phone: `+256700000001`

**2. Send initial request** (empty text)
- Show main menu: LegalBridge welcome + 5 options

**3. Navigate Boda Boda menu**
- Select 1 (Boda Boda)
- Show sub-menu
- Select 2 (I was stopped by police)
- Show END response with rights information

**4. Navigate Market Vendor menu**
- Restart session
- Select 2 (Market Vendor)
- Select 1 (Eviction notice)
- Show practical guidance in USSD format

**5. Language switch**
- Restart → Select 5 (Change Language) → Select 2 (Luganda)
- Show main menu in Luganda

**6. Find Legal Help**
- Navigate to option 4
- Show Uganda Law Society contact details in USSD

**Key talking points**:
- Works on any phone with no internet
- Same legal knowledge base as the mobile app
- For full document analysis → app is required
- Five languages: English, Luganda, Runyankore, Acholi, Lugbara
- Session state tracked throughout

---

## Handling Demo Questions

**"Can it really understand Luganda, Runyankore, Acholi or Lugbara?"**
> Voice recognition for local languages has known limitations. For this version, local-language support covers UI text and USSD menus. Voice STT uses Whisper, which is reliable in English only — the app shows a warning and asks users to confirm the transcription. We recommend recorded human prompts as fallback. New-language translations are first-pass drafts pending native-speaker review.

**"What if the AI makes up a law?"**
> The system uses RAG — it only cites provisions from documents we have manually approved and indexed. If no relevant source is found, it displays: "I cannot verify the applicable legal provision..." rather than inventing an answer.

**"Is this giving legal advice?"**
> No. The disclaimer appears on every explanation screen. LegalBridge provides legal information and navigation — it always directs users to qualified legal professionals for complex or serious matters.

**"How is user data protected?"**
> Phone number is the only required personal data. Users control their documents and can delete them. We comply with Uganda's Data Protection and Privacy Act 2019. Documents are not used to train AI models.

---

## Sample Documents

Place these in `legal_sources/sample_docs/`:

1. `sample_traffic_notice.jpg` — fictional traffic penalty notice
2. `sample_eviction_notice.jpg` — fictional market eviction notice
3. `sample_allocation_slip.jpg` — fictional market allocation slip
4. `sample_payment_receipt.jpg` — fictional market payment receipt

All documents must be clearly labelled "SAMPLE — FOR DEMONSTRATION ONLY"
with fictional names and reference numbers.
