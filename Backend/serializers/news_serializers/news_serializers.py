from rest_framework import serializers
from Backend.models.news_model.news_model import News


class NewsSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'url', 'media', 'author', 'slug', 'created_at']