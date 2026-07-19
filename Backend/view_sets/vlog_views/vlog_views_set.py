from rest_framework import viewsets
from Backend.models.vlogs_model.vlogs_model import Vlogs
from Backend.permissions.moderator_permissions.moderator_permission import ReadOnlyForEveryone
from Backend.serializers.vlogs_serializers.vlog_serializer import VlogsSerializer


class VlogsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VlogsSerializer
    permission_classes = [ReadOnlyForEveryone]

    def get_queryset(self):
        return Vlogs.objects.filter(is_published=True).select_related('author').order_by('-created_at')
