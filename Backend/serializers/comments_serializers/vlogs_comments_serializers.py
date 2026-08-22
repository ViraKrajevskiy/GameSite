from rest_framework import serializers
from Backend.models.comments_model.vlogs_coment import VlogsComment


class _AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.ImageField(required=False, allow_null=True)


class VlogsReplySerializer(serializers.ModelSerializer):
    author = _AuthorSerializer(source='vl_comment_author', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = VlogsComment
        fields = ['id', 'vlogs', 'parent', 'author', 'comment', 'is_mine', 'created_at', 'updated_at']
        read_only_fields = fields

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.vl_comment_author_id == request.user.id)


class VlogsCommentSerializer(serializers.ModelSerializer):
    author = _AuthorSerializer(source='vl_comment_author', read_only=True)
    replies = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = VlogsComment
        fields = ['id', 'vlogs', 'parent', 'author', 'comment', 'replies', 'is_mine',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'replies', 'is_mine', 'created_at', 'updated_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.vl_comment_author_id == request.user.id)

    def get_replies(self, obj):
        if obj.parent_id is not None:
            return []
        replies = obj.replies.select_related('vl_comment_author').order_by('created_at')
        return VlogsReplySerializer(replies, many=True, context=self.context).data

    def validate(self, attrs):
        parent = attrs.get('parent')
        if parent is not None:
            if parent.parent_id is not None:
                attrs['parent'] = parent.parent
            vlogs = attrs.get('vlogs') or getattr(self.instance, 'vlogs', None)
            if vlogs and attrs['parent'].vlogs_id != vlogs.id:
                raise serializers.ValidationError({'parent': 'Комментарий должен быть в том же влоге.'})
        return attrs

    def create(self, validated_data):
        validated_data['vl_comment_author'] = self.context['request'].user
        return super().create(validated_data)
