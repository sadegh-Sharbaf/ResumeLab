from django.db import connections
from django.http import JsonResponse


def healthcheck(request):
    """Small Render health endpoint that also verifies the database connection."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "connected"})
