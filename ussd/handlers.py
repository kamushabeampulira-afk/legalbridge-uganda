"""
LegalBridge USSD — Standalone handler reference.

The actual USSD handler lives in backend/channels_app/ussd_handler.py.
This file exists as a reference entry point per the project spec structure.

To test the handler directly:

    cd backend
    python -c "
    from channels_app.ussd_handler import handle_ussd_request
    # Simulate fresh session
    print(handle_ussd_request('sess001', '*384*0#', '+256700000001', ''))
    # Select Boda Boda
    print(handle_ussd_request('sess001', '*384*0#', '+256700000001', '1'))
    # Select stopped by police
    print(handle_ussd_request('sess001', '*384*0#', '+256700000001', '1*2'))
    "

For Africa's Talking integration, the webhook endpoint is:
    POST /api/ussd/webhook/

Configured in backend/channels_app/views.py and backend/channels_app/urls.py.
"""
