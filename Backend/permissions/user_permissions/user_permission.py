from rest_framework import permissions
from Backend.permissions.moderator_permissions.moderator_permission import IsAdminOrModerator


class CommentPermission(permissions.BasePermission):
    """
    Для NewsComment / VlogsComment.
    - Читать может любой (GET/HEAD/OPTIONS).
    - Создавать (POST) может любой авторизованный пользователь.
    - Редактировать/удалять ("банить") — только модератор или админ.
      Автор своего комментария менять/удалять не может.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        # PUT/PATCH/DELETE — дальше решает has_object_permission
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return IsAdminOrModerator.check(request.user)


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