import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


def _default_expires_at():
    return timezone.now() + timedelta(hours=24)


def _new_token():
    return secrets.token_urlsafe(48)


class PendingRegistration(models.Model):
    """
    Кандидат на регистрацию: пока пользователь не подтвердил email по ссылке,
    настоящий User не создаётся. Так мы не палим факт занятости email —
    endpoint регистрации отвечает одинаково и для новых, и для существующих
    адресов, а «уже занят» узнаём только владельцу почты через письмо.
    """
    email = models.EmailField()
    username = models.CharField(max_length=30)
    password_hash = models.CharField(max_length=128)
    token = models.CharField(max_length=96, unique=True, default=_new_token, db_index=True)
    expires_at = models.DateTimeField(default=_default_expires_at)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['email'])]
        verbose_name = 'Ожидающая регистрация'
        verbose_name_plural = 'Ожидающие регистрации'

    def __str__(self):
        return f'Pending {self.email} (expires {self.expires_at})'

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def purge_expired(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()
