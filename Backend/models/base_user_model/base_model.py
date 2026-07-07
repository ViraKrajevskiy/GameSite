from Backend.validators.base_user_validators.base_user_validators import (validate_email)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class TimeManager(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Created {self.created_at} , Updated {self.updated_at}"

    class Meta:
        abstract = True

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, TimeManager):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
        ('creator', 'Создатель контента'),
    ]

    email = models.EmailField(unique=True, validators=[validate_email])
    username = models.CharField(max_length=30, unique=True, validators=[...])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_moderator(self):
        return self.role == 'moderator'

    def is_creator(self):
        return self.role == 'creator'

    def has_perm(self, perm, obj=None):
        """Переопределенная проверка прав"""
        if self.is_superuser:
            return True
        return super().has_perm(perm, obj)