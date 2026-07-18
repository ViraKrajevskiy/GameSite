from rest_framework import serializers
from Backend.models.games_model.game_rating_models import GamesRating


class GamesRatingSerializer(serializers.ModelSerializer):
    rating_writer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GamesRating
        fields = ['id', 'game', 'rating_writer', 'text', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'rating_writer', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['rating_writer'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context['request']
        game = attrs.get('game')
        if request.method == 'POST' and game and GamesRating.objects.filter(
            game=game, rating_writer=request.user
        ).exists():
            raise serializers.ValidationError('Вы уже оценивали эту игру.')
        return attrs