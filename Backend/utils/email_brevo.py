"""
Отправка писем через Brevo HTTP API (не SMTP).

Почему не SMTP: DigitalOcean по умолчанию блокирует исходящие
подключения по портам 25/465/587 для новых аккаунтов, поэтому SMTP
через smtp-relay.brevo.com даёт TimeoutError. HTTP API работает
через 443/HTTPS — это никто не блокирует.

Настройки в .env:
  BREVO_API_KEY=xkeysib-...       (обязательно)
  DEFAULT_FROM_EMAIL=Vira Krajevskiy <thelastbreath2025st@gmail.com>

Если BREVO_API_KEY не задан — функция кидает RuntimeError, вызывающий
код должен ловить и продолжать (например, класть письмо в лог для дев-режима).
"""
import logging
import os
import re

import requests
from django.conf import settings

log = logging.getLogger(__name__)

BREVO_ENDPOINT = 'https://api.brevo.com/v3/smtp/email'
TIMEOUT_SECONDS = 12


def _parse_from(header_value: str):
    """
    Разбирает 'Name <email@x.com>' на dict {name, email}, как ждёт Brevo API.
    Если формат простой email — name будет None.
    """
    match = re.match(r'^\s*(.*?)\s*<([^>]+)>\s*$', header_value or '')
    if match:
        name, email = match.group(1).strip(), match.group(2).strip()
        return {'name': name, 'email': email} if name else {'email': email}
    email = (header_value or '').strip()
    return {'email': email}


def send_email_via_brevo(*, to_email: str, subject: str, text: str, html: str = None,
                         from_header: str = None) -> None:
    """
    Кидает письмо через HTTP API. Возвращает None при успехе, поднимает исключение
    при ошибке — вызывающий код сам решает, ловить или отдать пользователю дефолт.
    """
    api_key = os.getenv('BREVO_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('BREVO_API_KEY не задан в .env')

    sender = _parse_from(from_header or settings.DEFAULT_FROM_EMAIL)
    payload = {
        'sender': sender,
        'to': [{'email': to_email}],
        'subject': subject,
        'textContent': text,
    }
    if html:
        payload['htmlContent'] = html

    resp = requests.post(
        BREVO_ENDPOINT,
        json=payload,
        headers={
            'api-key': api_key,
            'accept': 'application/json',
            'content-type': 'application/json',
        },
        timeout=TIMEOUT_SECONDS,
    )
    if resp.status_code >= 300:
        # Логируем тело — Brevo даёт полезное сообщение об ошибке
        log.error('Brevo API returned %s: %s', resp.status_code, resp.text[:500])
        resp.raise_for_status()
