from django.db.models import Avg
from rest_framework import serializers
from Backend.models.games_model.games_model import Games


class GamesSerializer(serializers.ModelSerializer):
    platforms = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()

    class Meta:
        model = Games
        fields = [
            'id', 'title', 'description', 'image', 'url',
            'platforms', 'average_rating', 'ratings_count', 'created_at',
        ]

    def get_platforms(self, obj):
        return [p.title for p in obj.platforms.all()]

    def get_average_rating(self, obj):
        avg = getattr(obj, 'avg_rating', None)
        if avg is None:
            agg = obj.ratings.aggregate(avg=Avg('rating'))
            avg = agg['avg']
        return round(avg, 1) if avg is not None else None

    def get_ratings_count(self, obj):
        count = getattr(obj, 'ratings_count', None)
        if count is None:
            count = obj.ratings.count()
        return count
