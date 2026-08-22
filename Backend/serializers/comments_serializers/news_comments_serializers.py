from rest_framework import serializers
from Backend.models.comments_model.news_coment import NewsComment


class _AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.ImageField(required=False, allow_null=True)


class NewsReplySerializer(serializers.ModelSerializer):
    """Реплай без вложенных ответов — треды у нас одноуровневые."""
    author = _AuthorSerializer(source='comment_writer', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = NewsComment
        fields = ['id', 'news', 'parent', 'author', 'text', 'is_mine', 'created_at', 'updated_at']
        read_only_fields = fields

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.comment_writer_id == request.user.id)


class NewsCommentSerializer(serializers.ModelSerializer):
    author = _AuthorSerializer(source='comment_writer', read_only=True)
    replies = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = NewsComment
        fields = ['id', 'news', 'parent', 'author', 'text', 'replies', 'is_mine',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'replies', 'is_mine', 'created_at', 'updated_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.comment_writer_id == request.user.id)

    def get_replies(self, obj):
        if obj.parent_id is not None:
            return []
        replies = obj.replies.select_related('comment_writer').order_by('created_at')
        return NewsReplySerializer(replies, many=True, context=self.context).data

    def validate(self, attrs):
        parent = attrs.get('parent')
        if parent is not None:
            # Не глубже одного уровня: ответ на реплай превращаем в ответ на его родителя.
            if parent.parent_id is not None:
                attrs['parent'] = parent.parent
            news = attrs.get('news') or getattr(self.instance, 'news', None)
            if news and attrs['parent'].news_id != news.id:
                raise serializers.ValidationError({'parent': 'Комментарий должен быть в той же новости.'})
        return attrs

    def create(self, validated_data):
        validated_data['comment_writer'] = self.context['request'].user
        return super().create(validated_data)
