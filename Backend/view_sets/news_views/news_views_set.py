from rest_framework import viewsets
from Backend.models.news_model.news_model import News
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone
from Backend.serializers.news_serializers.news_serializers import NewsSerializer

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [ReadOnlyForEveryone]

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('author').order_by('-created_at')
