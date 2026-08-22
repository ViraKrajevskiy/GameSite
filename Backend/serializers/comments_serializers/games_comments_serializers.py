from rest_framework import serializers
from Backend.models.comments_model.games_comment import GamesComment


class _AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.ImageField(required=False, allow_null=True)


class GamesReplySerializer(serializers.ModelSerializer):
    author = _AuthorSerializer(source='games_comment_writer', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = GamesComment
        fields = ['id', 'games_news', 'parent', 'author', 'games_text', 'is_mine',
                  'created_at', 'updated_at']
        read_only_fields = fields

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.games_comment_writer_id == request.user.id)


class GamesCommentSerializer(serializers.ModelSerializer):
    author = _AuthorSerializer(source='games_comment_writer', read_only=True)
    replies = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = GamesComment
        fields = ['id', 'games_news', 'parent', 'author', 'games_text', 'replies',
                  'is_mine', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'replies', 'is_mine', 'created_at', 'updated_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.games_comment_writer_id == request.user.id)

    def get_replies(self, obj):
        if obj.parent_id is not None:
            return []
        replies = obj.replies.select_related('games_comment_writer').order_by('created_at')
        return GamesReplySerializer(replies, many=True, context=self.context).data

    def validate(self, attrs):
        parent = attrs.get('parent')
        if parent is not None:
            if parent.parent_id is not None:
                attrs['parent'] = parent.parent
            game = attrs.get('games_news') or getattr(self.instance, 'games_news', None)
            if game and attrs['parent'].games_news_id != game.id:
                raise serializers.ValidationError({'parent': 'Комментарий должен быть в той же игре.'})
        return attrs

    def create(self, validated_data):
        validated_data['games_comment_writer'] = self.context['request'].user
        return super().create(validated_data)
