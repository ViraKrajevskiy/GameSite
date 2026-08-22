"""
Регистрация по OWASP: не палим существующих пользователей.

POST /api/auth/register/
  всегда 200 OK с одинаковым сообщением. Если email свободен — пишем
  PendingRegistration и шлём письмо с подтверждением. Если email занят —
  ничего не создаём, а владельцу шлём уведомление «на ваш адрес пытались
  зарегистрироваться». Ответ у API одинаковый в обоих случаях, чтобы
  нельзя было по нему угадать, есть ли email в базе.

POST /api/auth/register/confirm/
  { token: ... } — активирует ожидающую регистрацию: создаёт настоящего
  User и удаляет pending. Токен живёт 24 часа.
"""
import logging

from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import IntegrityError

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from Backend.models import User, PendingRegistration
from Backend.serializers.registration_serializers.registration_serializer import (
    RegistrationRequestSerializer,
    RegistrationConfirmSerializer,
)

log = logging.getLogger(__name__)

GENERIC_RESPONSE = {
    'detail': (
        'Если данные корректны, мы отправили письмо со ссылкой для подтверждения. '
        'Проверьте почту (включая «Спам»).'
    ),
}

SITE_NAME = 'Vira Krajevskiy'


def _send_confirm_email(pending: PendingRegistration):
    """Ссылка активации → на фронт, тот дёргает /api/auth/register/confirm/"""
    confirm_url = f'{settings.FRONTEND_URL.rstrip("/")}/register/confirm/{pending.token}'
    ctx = {
        'username': pending.username,
        'confirm_url': confirm_url,
        'site_name': SITE_NAME,
    }
    subject = f'Подтверждение регистрации на {SITE_NAME}'
    body_txt = render_to_string('emails/registration_confirm.txt', ctx)
    body_html = render_to_string('emails/registration_confirm.html', ctx)

    msg = EmailMultiAlternatives(subject, body_txt, settings.DEFAULT_FROM_EMAIL, [pending.email])
    msg.attach_alternative(body_html, 'text/html')
    msg.send(fail_silently=False)


def _send_already_registered_email(email: str):
    login_url = f'{settings.FRONTEND_URL.rstrip("/")}/login'
    ctx = {'login_url': login_url, 'site_name': SITE_NAME}
    subject = f'На ваш email пытались зарегистрироваться — {SITE_NAME}'
    body_txt = render_to_string('emails/registration_already_exists.txt', ctx)
    body_html = render_to_string('emails/registration_already_exists.html', ctx)

    msg = EmailMultiAlternatives(subject, body_txt, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(body_html, 'text/html')
    msg.send(fail_silently=False)


@method_decorator(ratelimit(key='ip', rate='5/10m', method='POST', block=True), name='dispatch')
class RegistrationView(APIView):
    """POST /api/auth/register/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            # Валидация формата (регэксп email, длина пароля, символы username).
            # Занятость email/username сюда не попадает — её проверит логика ниже.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].lower()
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Всё что дальше — обёрнуто в широкий try/except: пользователь никогда
        # не должен увидеть 500 из-за проблем с SMTP, шаблонами и т.п.
        # Ответ всегда одинаковый и нейтральный, а причина падает в лог.
        try:
            # 1) Если такой пользователь уже есть — не создаём ничего, шлём
            #    уведомление владельцу и отвечаем нейтрально.
            if User.objects.filter(email__iexact=email).exists():
                try:
                    _send_already_registered_email(email)
                except Exception:
                    log.exception('Failed to send already-registered notice to %s', email)
                return Response(GENERIC_RESPONSE, status=status.HTTP_200_OK)

            # 2) Уникальность username проверяем отдельно — но снова не палим:
            #    отвечаем тем же GENERIC_RESPONSE и ничего не создаём.
            if User.objects.filter(username__iexact=username).exists():
                return Response(GENERIC_RESPONSE, status=status.HTTP_200_OK)

            # 3) email свободен — переписываем/создаём pending и шлём подтверждение.
            PendingRegistration.objects.filter(email__iexact=email).delete()
            try:
                pending = PendingRegistration.objects.create(
                    email=email,
                    username=username,
                    password_hash=make_password(password),
                )
            except IntegrityError:
                return Response(GENERIC_RESPONSE, status=status.HTTP_200_OK)

            try:
                _send_confirm_email(pending)
            except Exception:
                log.exception('Failed to send confirm email to %s', email)

        except Exception:
            # Что-то совсем неожиданное (например, БД лежит). Не палим детали.
            log.exception('Unexpected error in RegistrationView for %s', email)

        return Response(GENERIC_RESPONSE, status=status.HTTP_200_OK)


class RegistrationConfirmView(APIView):
    """POST /api/auth/register/confirm/  { token: '...' }"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'ok': False, 'reason': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']

        try:
            pending = PendingRegistration.objects.get(token=token)
        except PendingRegistration.DoesNotExist:
            return Response({'ok': False, 'reason': 'invalid'}, status=status.HTTP_404_NOT_FOUND)

        if pending.is_expired():
            pending.delete()
            return Response({'ok': False, 'reason': 'expired'}, status=status.HTTP_410_GONE)

        # Пока pending лежал 24ч, кто-то мог занять email/username по другой цепочке.
        # Тогда просто удаляем pending и говорим invalid, чтобы не палить причину.
        if (User.objects.filter(email__iexact=pending.email).exists()
                or User.objects.filter(username__iexact=pending.username).exists()):
            pending.delete()
            return Response({'ok': False, 'reason': 'invalid'}, status=status.HTTP_409_CONFLICT)

        user = User(email=pending.email, username=pending.username)
        user.password = pending.password_hash  # уже хеш, не вызываем set_password повторно
        user.save()
        pending.delete()

        return Response({'ok': True}, status=status.HTTP_201_CREATED)
