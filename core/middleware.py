from django.conf import settings
from django.http import HttpResponseBadRequest

class MaxUploadSizeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_upload_size = getattr(settings, 'MAX_FILE_SIZE_MB', 10) * 1024 * 1024  # Convert MB to bytes

    def __call__(self, request):
        if request.method == 'POST' and 'file' in request.FILES:
            file = request.FILES['file']
            if file.size > self.max_upload_size:
                return HttpResponseBadRequest(f"File size exceeds {settings.MAX_FILE_SIZE_MB} MB limit.")
        return self.get_response(request)