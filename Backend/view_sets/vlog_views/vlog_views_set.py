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
            return qs
        if user.is_authenticated:
            return qs.filter(Q(is_published=True) | Q(author=user))
        return qs.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
