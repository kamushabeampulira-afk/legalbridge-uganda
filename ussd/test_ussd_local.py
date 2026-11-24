"""
LegalBridge — Local USSD test script.
Simulates Africa's Talking webhook calls without needing the AT simulator.

Usage (from project root with backend venv active):
    cd backend
    python ..\ussd\test_ussd_local.py

Requirements: Django server must be running on http://127.0.0.1:8000
"""
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000/api/ussd/webhook/'
PHONE = '+256700000001'
SESSION_COUNTER = [0]


def new_session():
    SESSION_COUNTER[0] += 1
    return f'test_session_{SESSION_COUNTER[0]:04d}'


def ussd(session_id: str, text: str, label: str = '') -> str:
    try:
        resp = requests.post(BASE_URL, data={
            'sessionId': session_id,
            'serviceCode': '*384*0#',
            'phoneNumber': PHONE,
            'text': text,
        }, timeout=10)
        display = label or f"Input: '{text}'"
        print(f"\n{'─'*60}")
        print(f"► {display}")
        print(f"◄ {resp.text.strip()}")
        return resp.text.strip()
    except requests.ConnectionError:
        print("\nERROR: Could not connect to backend.")
        print("Make sure Django is running: python manage.py runserver")
        sys.exit(1)


def run_tests():
    print("=" * 60)
    print("LegalBridge USSD — Local Test Suite")
    print("=" * 60)

    # ── Test 1: Main menu ────────────────────────────────────────
    print("\n[TEST 1] Fresh session → main menu")
    sid = new_session()
    r = ussd(sid, '', 'Fresh session')
    assert 'CON' in r, "FAIL: Expected CON main menu"
    assert 'Boda' in r or 'LegalBridge' in r, "FAIL: Expected LegalBridge in menu"
    print("  PASS")

    # ── Test 2: Boda Boda menu ───────────────────────────────────
    print("\n[TEST 2] Select Boda Boda → sub-menu")
    r = ussd(sid, '1', 'Select Boda Boda (1)')
    assert 'CON' in r, "FAIL: Expected CON boda menu"
    print("  PASS")

    # ── Test 3: Boda → stopped by police ────────────────────────
    print("\n[TEST 3] Boda → Stopped by police → END response")
    r = ussd(sid, '1*2', 'Select stopped by police (1→2)')
    assert 'END' in r, "FAIL: Expected END response"
    print("  PASS")

    # ── Test 4: Market vendor ────────────────────────────────────
    print("\n[TEST 4] Market vendor → eviction notice → END")
    sid2 = new_session()
    ussd(sid2, '', 'Fresh session')
    ussd(sid2, '2', 'Select Market Vendor (2)')
    r = ussd(sid2, '2*1', 'Select Eviction notice (2→1)')
    assert 'END' in r, "FAIL: Expected END response"
    print("  PASS")

    # ── Test 5: Legal help ───────────────────────────────────────
    print("\n[TEST 5] Find Legal Help → END with org details")
    sid3 = new_session()
    ussd(sid3, '', 'Fresh session')
    r = ussd(sid3, '4', 'Select Legal Help (4)')
    assert 'END' in r, "FAIL: Expected END response"
    assert 'Uganda Law Society' in r or 'Legal' in r, "FAIL: Expected legal org"
    print("  PASS")

    # ── Test 6: Language switch to Luganda ───────────────────────
    print("\n[TEST 6] Change language to Luganda")
    sid4 = new_session()
    ussd(sid4, '', 'Fresh session')
    ussd(sid4, '5', 'Select Change Language (5)')
    r = ussd(sid4, '5*2', 'Select Luganda (5→2)')
    assert 'CON' in r or 'Boda' in r or 'Akatale' in r, "FAIL: Expected Luganda menu"
    print("  PASS")

    # ── Test 7: Back navigation ──────────────────────────────────
    print("\n[TEST 7] Navigate into sub-menu then back")
    sid5 = new_session()
    ussd(sid5, '', 'Fresh session')
    ussd(sid5, '1', 'Into Boda Boda')
    r = ussd(sid5, '1*0', 'Press back (0)')
    assert 'CON' in r, "FAIL: Expected back to main CON menu"
    assert 'Boda' in r or 'Market' in r or 'LegalBridge' in r, "FAIL: Expected main menu"
    print("  PASS")

    # ── Test 8: Invalid selection ────────────────────────────────
    print("\n[TEST 8] Invalid selection → re-shows menu")
    sid6 = new_session()
    ussd(sid6, '', 'Fresh session')
    r = ussd(sid6, '9', 'Invalid selection (9)')
    assert 'CON' in r or 'END' in r, "FAIL: Expected valid USSD response"
    print("  PASS")

    print("\n" + "=" * 60)
    print("All USSD tests passed!")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()
