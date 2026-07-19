from rest_framework import serializers
from Backend.models.base_user_model.base_model import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'avatar', 'bio', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']
