from django.conf import settings

def gtag_processor(request):
    return {
        'GTAG_ENABLE': getattr(settings, 'GTAG_ENABLE', False),
        'GTAG_ID': getattr(settings, 'GTAG_ID', False)
    }