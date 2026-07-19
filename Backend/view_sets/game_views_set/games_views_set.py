from django.db.models import Avg, Count
from rest_framework import viewsets
from Backend.models.games_model.games_model import Games
from Backend.serializers.games_serializers.games_serializer import GamesSerializer
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone


class GamesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GamesSerializer
    permission_classes = [ReadOnlyForEveryone]

    def get_queryset(self):
        return (
            Games.objects
            .all()
            .prefetch_related('platforms')
            .annotate(avg_rating=Avg('ratings__rating'), ratings_count=Count('ratings', distinct=True))
            .order_by('-created_at')
        )
