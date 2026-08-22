"""
Сброс пароля по OWASP-стилю (симметрично регистрации).

POST /api/auth/password/reset/
  { email } → всегда 200 с нейтральным сообщением. Если email в базе —
  создаётся PendingPasswordReset (2 часа TTL) и уходит письмо со ссылкой.
  Если email не в базе — ничего не делаем, ответ тот же.

POST /api/auth/password/reset/confirm/
  { token, new_password } → 200 если токен валиден и не просрочен, иначе
  { ok: false, reason: 'invalid'|'expired' }.
"""
import logging

from django.template.loader import render_to_string
from django.conf import settings

from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from Backend.models import User, PendingPasswordReset
from Backend.utils.email_brevo import send_email_via_brevo

log = logging.getLogger(__name__)

GENERIC_RESPONSE = {
    'detail': (
        'Если такой email зарегистрирован, мы отправили на него ссылку для '
        'сброса пароля. Проверьте почту (включая «Спам»).'
    ),
}

SITE_NAME = 'Vira Krajevskiy'


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=96)
    new_password = serializers.CharField(min_length=8, write_only=True)


def _send_reset_email(user, token):
    reset_url = f'{settings.FRONTEND_URL.rstrip("/")}/password/reset/{token}'
    ctx = {
        'username': user.username,
        'reset_url': reset_url,
        'site_name': SITE_NAME,
    }
    send_email_via_brevo(
        to_email=user.email,
        subject=f'Сброс пароля на {SITE_NAME}',
        text=render_to_string('emails/password_reset.txt', ctx),
        html=render_to_string('emails/password_reset.html', ctx),
    )


@method_decorator(ratelimit(key='ip', rate='5/10m', method='POST', block=True), name='dispatch')
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].lower()

        try:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                # Убиваем старые токены этого юзера, чтобы одновременно жила
                # только одна ссылка сброса.
                PendingPasswordReset.objects.filter(user=user).delete()
                reset = PendingPasswordReset.objects.create(user=user)
                try:
                    _send_reset_email(user, reset.token)
                except Exception:
                    log.exception('Failed to send reset email to %s', email)
            # если пользователя нет — молча ничего не делаем
        except Exception:
            log.exception('Unexpected error in PasswordResetRequestView for %s', email)

        return Response(GENERIC_RESPONSE, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'ok': False, 'reason': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            reset = PendingPasswordReset.objects.select_related('user').get(token=token)
        except PendingPasswordReset.DoesNotExist:
            return Response({'ok': False, 'reason': 'invalid'}, status=status.HTTP_404_NOT_FOUND)

        if reset.is_expired():
            reset.delete()
            return Response({'ok': False, 'reason': 'expired'}, status=status.HTTP_410_GONE)

        user = reset.user
        user.set_password(new_password)
        user.save(update_fields=['password'])
        reset.delete()

        return Response({'ok': True}, status=status.HTTP_200_OK)
