from rest_framework import serializers

from Backend.validators.base_user_validators.base_user_validators import (
    validate_email,
    username_validator,
    username_length_validator,
    validate_username,
)


class RegistrationRequestSerializer(serializers.Serializer):
    """
    Валидирует только формат данных. Занятость email/username НЕ проверяем
    здесь — это могло бы палить существующих пользователей через сообщение
    об ошибке. Уникальность разруливается уже во view.
    """
    email = serializers.EmailField(validators=[validate_email])
    username = serializers.CharField(
        max_length=30,
        validators=[username_validator, username_length_validator, validate_username],
    )
    password = serializers.CharField(min_length=8, write_only=True)


class RegistrationConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=96)
