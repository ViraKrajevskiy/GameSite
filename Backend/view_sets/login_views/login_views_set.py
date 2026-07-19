from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from Backend.serializers.login_serializer.login_serializer import LoginSerializer
from Backend.serializers.user_serializers.user_serializer import UserSerializer

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class RefreshTokenView(TokenRefreshView):
    pass

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
