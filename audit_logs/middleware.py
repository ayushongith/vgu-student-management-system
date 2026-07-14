import threading

_local = threading.local()


def get_current_user():
    return getattr(_local, 'user', None)


def get_current_ip():
    return getattr(_local, 'ip', None)


class AuditRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.user = request.user if request.user.is_authenticated else None
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        _local.ip = ip
        
        response = self.get_response(request)
        
        if hasattr(_local, 'user'):
            del _local.user
        if hasattr(_local, 'ip'):
            del _local.ip
            
        return response
