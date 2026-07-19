from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from Backend.view_sets.registation_views.registation_views_set import RegistrationView
from Backend.view_sets.login_views.login_views_set import LoginView, RefreshTokenView, MeView
from Backend.view_sets.comments_views.comment_views_set import NewsCommentViewSet, VlogsCommentViewSet
from Backend.view_sets.game_views_set.game_rating_views_set import GamesRatingViewSet
from Backend.view_sets.news_views.news_views_set import NewsViewSet
from Backend.views import home
from Backend.view_sets.game_views_set.games_views_set import GamesViewSet
from Backend.view_sets.vlog_views.vlog_views_set import VlogsViewSet

router = DefaultRouter()
router.register(r'news-comments', NewsCommentViewSet, basename='news-comments')
router.register(r'vlogs-comments', VlogsCommentViewSet, basename='vlogs-comments')
router.register(r'game-ratings', GamesRatingViewSet, basename='game-ratings')
router.register(r'games', GamesViewSet, basename='games')
router.register(r'news', NewsViewSet, basename='news')
router.register(r'vlogs', VlogsViewSet, basename='vlogs')


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/auth/register/', RegistrationView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/login/refresh/', RefreshTokenView.as_view(), name='login-refresh'),
    path('api/auth/me/', MeView.as_view(), name='me'),

    path('api/', include(router.urls)),

    path('', home, name='home'),
]

