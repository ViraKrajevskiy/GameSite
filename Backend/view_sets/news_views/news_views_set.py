from django.db.models import Q
from rest_framework import viewsets

from Backend.models.news_model.news_model import News
from Backend.permissions.content_permissions.content_permission import ContentPermission
from Backend.serializers.news_serializers.news_serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    Раньше был ReadOnlyModelViewSet — создать новость через API было нельзя
    в принципе, только через админку. Теперь создатель контента и админ
    работают через API, остальные по-прежнему только читают (ContentPermission).
    """
    serializer_class = NewsSerializer
    permission_classes = [ContentPermission]

    def get_queryset(self):
        qs = News.objects.select_related('author').order_by('-created_at')
        user = self.request.user

        # Админ и модератор видят всё, включая черновики
        if user.is_authenticated and (user.is_admin() or user.is_moderator()):
            return self._by_kind(qs)
        # Автор видит свои черновики — иначе он не найдёт то, что только что создал
        if user.is_authenticated:
            qs = qs.filter(Q(is_published=True) | Q(author=user))
        else:
            qs = qs.filter(is_published=True)

        return self._by_kind(qs)

    def _by_kind(self, queryset):
        """?kind=devlog и т.д. — фильтр списка по разделу."""
        kind = self.request.query_params.get('kind')
        return queryset.filter(kind=kind) if kind else queryset

    def perform_create(self, serializer):
        # Автора берём из запроса, а не из тела — иначе можно подписаться чужим именем
        serializer.save(author=self.request.user)
