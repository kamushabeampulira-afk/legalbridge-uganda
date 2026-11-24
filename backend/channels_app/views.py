"""
LegalBridge — Africa's Talking USSD webhook view.
Africa's Talking sends POST requests with form-encoded data.
Response must be plain text starting with CON (continue) or END (terminate).
"""
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .ussd_handler import handle_ussd_request
from .models import USSDSession

logger = logging.getLogger('legalbridge')


@csrf_exempt
@require_POST
def ussd_webhook(request):
    """
    POST /api/ussd/webhook/
    Africa's Talking posts these fields:
    - sessionId
    - serviceCode
    - phoneNumber
    - text  (accumulated input, e.g. '1*2*3')
    """
    try:
        session_id = request.POST.get('sessionId', '')
        service_code = request.POST.get('serviceCode', '')
        phone_number = request.POST.get('phoneNumber', '')
        text = request.POST.get('text', '')

        if not session_id or not phone_number:
            logger.warning('USSD webhook called with missing sessionId or phoneNumber')
            return HttpResponse('END Invalid request.', content_type='text/plain')

        logger.info(f'USSD request: session={session_id}, phone={phone_number}, text="{text}"')

        response_text = handle_ussd_request(
            session_id=session_id,
            service_code=service_code,
            phone_number=phone_number,
            text=text,
        )

        # Log the session asynchronously (fire and forget for MVP)
        try:
            ended = response_text.startswith('END')
            USSDSession.objects.update_or_create(
                session_id=session_id,
                defaults={
                    'phone_number': phone_number,
                    'service_code': service_code,
                    'input_text': text,
                    'response_text': response_text[:1000],
                    'ended': ended,
                }
            )
        except Exception as log_err:
            logger.warning(f'Could not log USSD session: {log_err}')

        return HttpResponse(response_text, content_type='text/plain')

    except Exception as e:
        logger.error(f'USSD webhook fatal error: {e}')
        return HttpResponse(
            'END Sorry, service is temporarily unavailable. Please try again.',
            content_type='text/plain'
        )
