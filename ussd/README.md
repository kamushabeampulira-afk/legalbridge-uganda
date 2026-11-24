# LegalBridge USSD Integration

The USSD system is built into the Django backend (`channels_app`).
This directory contains standalone documentation and test scripts.

## Architecture

```
Mobile user dials *384*0#
        │
        ▼
Africa's Talking Gateway
        │  POST (sessionId, phoneNumber, text)
        ▼
POST /api/ussd/webhook/
        │
        ▼
channels_app/views.py → ussd_handler.py
        │
        ├── _get_session()     (Django cache / Redis)
        ├── handle_ussd_request()
        ├── _render_menu()     (ussd_menus.py)
        └── _save_session()
        │
        ▼
Plain text response: "CON ..." or "END ..."
        │
        ▼
Africa's Talking displays to user
```

## Menu Tree

```
*384*0#
├── 1. Boda Boda Rider
│   ├── 1. Traffic violation notice     [END]
│   ├── 2. I was stopped by police      [END]
│   ├── 3. Understand a penalty         [END]
│   ├── 4. Payment procedure            [END]
│   └── 0. Back
├── 2. Market Vendor
│   ├── 1. Eviction notice              [END]
│   ├── 2. My allocation slip           [END]
│   ├── 3. Payment receipt help         [END]
│   ├── 4. Market vendor rights         [END]
│   └── 0. Back
├── 3. Know Your Rights
│   ├── 1. Traffic laws                 [END]
│   ├── 2. Market vendor rights         [END]
│   ├── 3. Employment information       [END]
│   ├── 4. Other legal information      [END]
│   └── 0. Back
├── 4. Find Legal Help                  [END]
└── 5. Change Language
    ├── 1. English
    ├── 2. Luganda
    ├── 3. Runyankore
    ├── 4. Acholi
    └── 5. Lugbara
```

## Development Setup

### 1. Configure Africa's Talking sandbox
```
AT_USERNAME=sandbox
AT_API_KEY=your-sandbox-api-key
AT_ENVIRONMENT=sandbox
```

### 2. Expose local server
```bash
ngrok http 8000
```

### 3. Set AT webhook URL
In AT sandbox dashboard:
- USSD → Create service
- Shortcode: *384*0#
- Callback URL: https://xxxx.ngrok.io/api/ussd/webhook/

### 4. Test with AT simulator
https://simulator.africastalking.com/

## Session Management

Sessions use Django's cache framework:
- **Development**: LocMemCache (in-memory, lost on restart)
- **Production**: Redis cache (persistent, shared across workers)

Session TTL: 300 seconds (5 minutes — standard USSD timeout)

To configure Redis in production, add to `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

And use `config/settings_production.py`.

## USSD Character Limits

- Maximum response length: ~182 characters per screen
- All menu text is designed to fit within this limit
- Long legal information directs users to the mobile app

## Language Support

- English, Luganda, Runyankore, Acholi and Lugbara available
- Language persisted per session in cache
- Changed via "Change Language" menu option (option 5)
- Deep menus not yet translated are shown in English; add a language-code key
  to the menu in `ussd_menus.py` to translate it
- Africa's Talking only transports the USSD text — it does not translate it

## Testing USSD Locally (without AT)

```python
# Python test script — simulates AT webhook calls
import requests

BASE_URL = 'http://127.0.0.1:8000/api/ussd/webhook/'

def ussd_call(session_id, text):
    response = requests.post(BASE_URL, data={
        'sessionId': session_id,
        'serviceCode': '*384*0#',
        'phoneNumber': '+256700000001',
        'text': text,
    })
    print(f"Input: '{text}'")
    print(f"Response:\n{response.text}")
    print("---")

# Simulate a full session
ussd_call('test001', '')           # Fresh session → main menu
ussd_call('test001', '1')          # Boda Boda menu
ussd_call('test001', '1*2')        # Boda → Stopped by police
```

## Production Checklist

- [ ] Set `AT_ENVIRONMENT=production`
- [ ] Update AT_API_KEY to production key
- [ ] Register shortcode with Uganda Communications Commission
- [ ] Configure Redis for session persistence
- [ ] Set up monitoring for USSD session failures
- [ ] Test all menu paths before go-live
- [ ] Verify character counts on all END screens
