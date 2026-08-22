"""
RealIPMiddleware — переписывает REMOTE_ADDR настоящим IP клиента.

Nginx проксирует запросы на gunicorn через unix-socket, поэтому в
REMOTE_ADDR у Django пусто. Реальный IP клиента nginx кладёт в заголовок
X-Forwarded-For (nginx-конфиг: proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for).

Без этого middleware любой код, который читает REMOTE_ADDR (например
django-ratelimit), падает с ImproperlyConfigured.

X-Forwarded-For — это список через запятую (client, proxy1, proxy2).
Берём самый левый, это адрес самого клиента.

Middleware должен стоять в самом верху MIDDLEWARE, до всего что читает
REMOTE_ADDR или client IP.
"""


class RealIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if xff:
            request.META['REMOTE_ADDR'] = xff.split(',')[0].strip()
        else:
            # запасной вариант: X-Real-IP от nginx
            xri = request.META.get('HTTP_X_REAL_IP', '').strip()
            if xri:
                request.META['REMOTE_ADDR'] = xri
        return self.get_response(request)
