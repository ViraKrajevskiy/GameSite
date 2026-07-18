from rest_framework import serializers
from Backend.models.comments_model.news_coment import NewsComment

class NewsCommentSerializer(serializers.ModelSerializer):
    comment_writer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NewsComment
        fields = ['id', 'news', 'comment_writer', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'comment_writer', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['comment_writer'] = self.context['request'].user
        return super().create(validated_data)