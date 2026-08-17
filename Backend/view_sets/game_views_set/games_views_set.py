from django.db.models import Avg, Count
from rest_framework import viewsets
from Backend.models.games_model.games_model import Games
from Backend.serializers.games_serializers.games_serializer import GamesSerializer
from Backend.permissions.content_permissions.content_permission import ContentPermission


class GamesViewSet(viewsets.ModelViewSet):
    """
    Каталог игр. Раньше был ReadOnlyModelViewSet — добавить игру через API
    не мог никто, включая суперюзера. Теперь чтение доступно всем, а запись —
    создателю контента и админу (ContentPermission).

    Автора у Games нет: это общий каталог, а не личные публикации.
    """
    serializer_class = GamesSerializer
    permission_classes = [ContentPermission]

    def get_serializer_context(self):
        # нужен request, чтобы отдавать абсолютные ссылки на картинки платформ
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = (
            Games.objects
            .all()
            .prefetch_related('platform_releases__platform', 'versions', 'links')
            .annotate(avg_rating=Avg('ratings__rating'), ratings_count=Count('ratings', distinct=True))
            .order_by('-created_at')
        )

        # ?kind=game / desktop / web / mobile / other — фильтр каталога по типу
        kind = self.request.query_params.get('kind')
        if kind:
            queryset = queryset.filter(kind=kind)

        return queryset
