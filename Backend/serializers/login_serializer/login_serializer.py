from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """
    Логин по email/паролю (USERNAME_FIELD = 'email' у User).
    Помимо access/refresh токенов возвращает базовые данные пользователя,
    чтобы фронтенду не нужно было делать отдельный запрос сразу после логина.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'role': self.user.role,
            'avatar': self.user.avatar.url if self.user.avatar else None,
        }
        return data
