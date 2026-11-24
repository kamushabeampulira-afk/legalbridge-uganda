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

## Demo 2b: Free Legal Aid Connection

**Available from**: Home → **Free Legal Aid**, the voice screen → **Connect to Legal Aid**, and inside **Find Legal Help**.

### Steps

1. Open Free Legal Aid (or Find Legal Help)
2. Choose a district, e.g. **Kampala** or **Buikwe**
3. Show the published area office:
   - Kampala → Mmengo Justice Centre (`0800 100 210`, `0800 100 225`, `0759 500 440`)
   - Buikwe → Mukono Justice Centre (`0800 100 218`, `0707 500 448`)
4. Try a district without a published centre number, e.g. **Gulu** — the app says no verified area office is listed yet
5. Show **Extra help**: Counsel Doug (`+256784122995`, Legal Officer) and the toll-free line (`+256323303969`)

**Key talking points**:
- Area office numbers come from the published Justice Centres Uganda contacts list
- Districts with no published office number are not given a fake fallback
- Doug and the toll-free line are clearly labelled extra help, not the district office
- Every static label works in English and Luganda

**Source**: https://justicecentres.go.ug/contacts/

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
> Voice recognition for local languages has known limitations. Whisper has no Luganda language code (the API rejects `language=lg`), so the backend sends a prompt hint instead of a language hint — without it, Whisper can hallucinate an unrelated English sentence. Accuracy is limited for all local languages, so the app flags this and lets the user **edit the transcript before submitting**. On web, answers are spoken with browser speech synthesis — no API key needed; a device voice is used when available, otherwise the closest available voice. Local-language support currently covers UI text and USSD menus; Runyankore, Acholi and Lugbara strings are first-pass drafts pending native-speaker review. For a guaranteed local-language voice, use a pre-recorded human prompt as fallback.

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
