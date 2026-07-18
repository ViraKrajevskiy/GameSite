from rest_framework import viewsets
from Backend.models.games_model.game_rating_models import GamesRating
from Backend.serializers.games_serializers.game_rations_serializers import GamesRatingSerializer
from Backend.permissions.user_permissions.user_permission import RatingPermission


class GamesRatingViewSet(viewsets.ModelViewSet):
    queryset = GamesRating.objects.all()
    serializer_class = GamesRatingSerializer
    permission_classes = [RatingPermission]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']