from django.db.models import Avg, Count
from rest_framework import viewsets
from Backend.models.games_model.games_model import Games
from Backend.serializers.games_serializers.games_serializer import GamesSerializer
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone


class GamesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GamesSerializer
    permission_classes = [ReadOnlyForEveryone]

    def get_serializer_context(self):
        # нужен request, чтобы отдавать абсолютные ссылки на картинки платформ
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = (
            Games.objects
            .all()
            .prefetch_related('platform_releases__platform')
            .annotate(avg_rating=Avg('ratings__rating'), ratings_count=Count('ratings', distinct=True))
            .order_by('-created_at')
        )

        # ?kind=game / desktop / web / mobile / other — фильтр каталога по типу
        kind = self.request.query_params.get('kind')
        if kind:
            queryset = queryset.filter(kind=kind)

        return queryset
