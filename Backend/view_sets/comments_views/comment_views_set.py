from rest_framework import viewsets

from Backend.models.comments_model.news_coment import NewsComment
from Backend.models.comments_model.vlogs_coment import VlogsComment
from Backend.models.comments_model.games_comment import GamesComment

from Backend.serializers.comments_serializers.news_comments_serializers import NewsCommentSerializer
from Backend.serializers.comments_serializers.vlogs_comments_serializers import VlogsCommentSerializer
from Backend.serializers.comments_serializers.games_comments_serializers import GamesCommentSerializer

from Backend.permissions.user_permissions.user_permission import CommentPermission


class NewsCommentViewSet(viewsets.ModelViewSet):
    queryset = NewsComment.objects.select_related('comment_writer').prefetch_related('replies__comment_writer')
    serializer_class = NewsCommentSerializer
    permission_classes = [CommentPermission]
    # Автор может править и удалять свой комментарий; модератор — удалить любой.
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        news_id = self.request.query_params.get('news')
        if news_id:
            qs = qs.filter(news_id=news_id)
        # На список отдаём только корневые; реплаи придут вложенным полем replies.
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
        return qs


class VlogsCommentViewSet(viewsets.ModelViewSet):
    queryset = VlogsComment.objects.select_related('vl_comment_author').prefetch_related('replies__vl_comment_author')
    serializer_class = VlogsCommentSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        vlogs_id = self.request.query_params.get('vlogs')
        if vlogs_id:
            qs = qs.filter(vlogs_id=vlogs_id)
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
        return qs


class GamesCommentViewSet(viewsets.ModelViewSet):
    queryset = GamesComment.objects.select_related('games_comment_writer').prefetch_related('replies__games_comment_writer')
    serializer_class = GamesCommentSerializer
    permission_classes = [CommentPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        game_id = self.request.query_params.get('games_news') or self.request.query_params.get('game')
        if game_id:
            qs = qs.filter(games_news_id=game_id)
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
        return qs
