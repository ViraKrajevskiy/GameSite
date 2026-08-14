from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Backend.models.home_model.home_model import HomeHero
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone
from Backend.serializers.home_serializers.home_serializer import HomeHeroSerializer


class HomeHeroView(APIView):
    """
    GET /api/hero/ — первый экран главной страницы.

    Редактируется через админку (/admin/ → Главная: первый экран), API только читает.
    """

    permission_classes = [ReadOnlyForEveryone]
    serializer_class = HomeHeroSerializer

    def get(self, request):
        hero = (
            HomeHero.objects
            .filter(is_active=True)
            .prefetch_related('stats')
            .order_by('-updated_at')
            .first()
        )

        if hero is None:
            return Response(
                {'detail': 'Активный первый экран не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(HomeHeroSerializer(hero, context={'request': request}).data)
