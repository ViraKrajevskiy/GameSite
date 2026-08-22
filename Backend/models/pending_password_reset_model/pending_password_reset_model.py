import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


def _default_expires_at():
    # Ссылки сброса пароля живут меньше, чем регистрационные — 2 часа хватает
    return timezone.now() + timedelta(hours=2)


def _new_token():
    return secrets.token_urlsafe(48)


class PendingPasswordReset(models.Model):
    """
    Токен на сброс пароля. Создаётся по запросу /api/auth/password/reset/,
    активируется в /api/auth/password/reset/confirm/ вместе с новым паролем.

    Пароль не хранится — только токен и user_id. Пока токен жив, любой
    предъявитель сможет задать пользователю новый пароль. Поэтому короткий
    TTL (2 часа) и одноразовое использование (удаляется после применения).
    """
    user = models.ForeignKey(
        'Backend.User', on_delete=models.CASCADE, related_name='password_resets',
    )
    token = models.CharField(max_length=96, unique=True, default=_new_token, db_index=True)
    expires_at = models.DateTimeField(default=_default_expires_at)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Токен сброса пароля'
        verbose_name_plural = 'Токены сброса пароля'

    def __str__(self):
        return f'PasswordReset for {self.user.email} (expires {self.expires_at})'

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def purge_expired(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()
