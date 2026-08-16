from django.db.models import Q
from rest_framework import viewsets

from Backend.models.vlogs_model.vlogs_model import Vlogs
from Backend.permissions.content_permissions.content_permission import ContentPermission
from Backend.serializers.vlogs_serializers.vlog_serializer import VlogsSerializer


class VlogsViewSet(viewsets.ModelViewSet):
    """
    Как и NewsViewSet: чтение — всем, запись — создателю контента и админу.
    """
    serializer_class = VlogsSerializer
    permission_classes = [ContentPermission]

    def get_queryset(self):
        qs = Vlogs.objects.select_related('author').order_by('-created_at')
        user = self.request.user

        if user.is_authenticated and (user.is_admin() or user.is_moderator()):
            return self._by_kind(qs)
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
        serializer.save(author=self.request.user)
