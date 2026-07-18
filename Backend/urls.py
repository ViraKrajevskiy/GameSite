from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from Backend.view_sets.registation_views.registation_views_set import RegistrationView
from Backend.view_sets.login_views.login_views_set import LoginView, RefreshTokenView
from Backend.view_sets.comments_views.comment_views_set import NewsCommentViewSet, VlogsCommentViewSet
from Backend.view_sets.game_views_set.game_rating_views_set import GamesRatingViewSet
from Backend.views import home


router = DefaultRouter()
router.register(r'news-comments', NewsCommentViewSet, basename='news-comments')
router.register(r'vlogs-comments', VlogsCommentViewSet, basename='vlogs-comments')
router.register(r'game-ratings', GamesRatingViewSet, basename='game-ratings')


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/auth/register/', RegistrationView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/login/refresh/', RefreshTokenView.as_view(), name='login-refresh'),

    path('', home, name='home'),
]

urlpatterns += router.urls