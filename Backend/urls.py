from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from Backend.view_sets.registation_views.registation_views_set import RegistrationView
from Backend.view_sets.login_views.login_views_set import LoginView, RefreshTokenView
from Backend.views import home


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/auth/register/', RegistrationView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/login/refresh/', RefreshTokenView.as_view(), name='login-refresh'),


    path('',home,name='home'),
]