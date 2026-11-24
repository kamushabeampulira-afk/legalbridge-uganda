"""Lightweight health check for deployment platforms such as Render."""
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache


@never_cache
def healthz(_request):
    """Return 200 when the app can import, route and reach PostgreSQL."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return HttpResponse('db unavailable', status=503, content_type='text/plain')
    return HttpResponse('ok', content_type='text/plain')
