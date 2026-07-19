from rest_framework import serializers
from Backend.models.vlogs_model.vlogs_model import Vlogs


class VlogsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='vlog_title', read_only=True)
    description = serializers.CharField(source='text', read_only=True)
    embed_url = serializers.URLField(source='url', read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Vlogs
        fields = ['id', 'title', 'description', 'embed_url', 'media', 'author', 'slug', 'created_at']