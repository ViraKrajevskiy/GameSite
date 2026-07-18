from rest_framework import viewsets
from Backend.models.comments_model.news_coment import NewsComment
from Backend.models.comments_model.vlogs_coment import VlogsComment
from Backend.serializers.comments_serializers.news_comments_serializers import NewsCommentSerializer
from Backend.serializers.comments_serializers.vlogs_comments_serializers import VlogsCommentSerializer
from Backend.permissions.user_permissions.user_permission import CommentPermission


class NewsCommentViewSet(viewsets.ModelViewSet):
    queryset = NewsComment.objects.all()
    serializer_class = NewsCommentSerializer
    permission_classes = [CommentPermission]
    # PUT/PATCH из API вообще не даём делать никому, кроме бана (удаления) модератором
    http_method_names = ['get', 'post', 'delete', 'head', 'options']


class VlogsCommentViewSet(viewsets.ModelViewSet):
    queryset = VlogsComment.objects.all()
    serializer_class = VlogsCommentSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']