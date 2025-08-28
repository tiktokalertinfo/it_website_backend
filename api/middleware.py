from django.conf import settings
from django.http import JsonResponse

class K1NG0FTHEH1LL:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if getattr(settings, 'SITE_LOCKED', False):
            if not request.user.is_superuser:
                return JsonResponse({"success": False, "error": "1191"}, status=503)
        return self.get_response(request)
