from rest_framework import permissions
from Backend.permissions.moderator_permissions.moderator_permission import IsAdminOrModerator


class CommentPermission(permissions.BasePermission):
    """
    Для NewsComment / VlogsComment / GamesComment.
    - Читать может любой (GET/HEAD/OPTIONS).
    - Создавать (POST) — любой авторизованный пользователь.
    - Редактировать (PATCH/PUT) свой комментарий — сам автор.
      Модератору редактировать чужие смысла нет.
    - Удалять (DELETE) — автор своего или модератор/админ любой (бан).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def _author(self, obj):
        # У всех трёх моделей поле автора называется по-разному
        for attr in ('comment_writer', 'vl_comment_author', 'games_comment_writer'):
            author = getattr(obj, attr, None)
            if author is not None:
                return author
        return None

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        author = self._author(obj)
        if request.method in ('PUT', 'PATCH'):
            # только сам автор может редактировать свой комментарий
            return author == request.user
        if request.method == 'DELETE':
            return author == request.user or IsAdminOrModerator.check(request.user)
        return False


class RatingPermission(permissions.BasePermission):
    """
    Для GamesRating.
    - Читать может любой.
    - Создавать (POST) может любой авторизованный пользователь.
    - Редактировать/удалять свою оценку может сам автор.
    - Модератор/админ может удалить ("забанить") любую оценку.
    - Чужую оценку обычный пользователь менять/удалять не может.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if IsAdminOrModerator.check(request.user):
            return True
        return obj.rating_writer == request.user