from rest_framework import generics, permissions
from Backend.serializers.registration_serializers.registration_serializer import RegistrationSerializer

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
