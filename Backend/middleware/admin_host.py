"""
Админка отвечает только на своём хосте.

На боевом сервере nginx уже отдаёт 404 на /admin/ для основного домена,
но одного слоя мало: конфиг nginx легко затереть при переустановке certbot
или неудачном деплое, и тогда админка снова окажется на главном домене.
Здесь та же проверка живёт в самом приложении.

DJANGO_ADMIN_HOST не задан (локальная разработка) — middleware не мешает.
"""

import os

from django.http import Http404


class AdminHostMiddleware:
    """404 на /admin/, если запрос пришёл не на админский хост."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_host = os.getenv('DJANGO_ADMIN_HOST', '').strip().lower()

    def __call__(self, request):
        if self.admin_host and self._is_admin_path(request.path):
            # get_host() отдаёт хост с портом — порт для сравнения не нужен
            host = request.get_host().split(':')[0].lower()
            if host != self.admin_host:
                raise Http404

        return self.get_response(request)

    @staticmethod
    def _is_admin_path(path: str) -> bool:
        # именно /admin и /admin/..., а не /administrators/
        return path == '/admin' or path.startswith('/admin/')
