from rest_framework import permissions


class IsAdminOrModerator(permissions.BasePermission):
    """Проверка роли — используется как строительный блок в других пермишенах."""

    @staticmethod
    def check(user):
        return bool(user and user.is_authenticated and (user.is_admin() or user.is_moderator()))


class ReadOnlyForEveryone(permissions.BasePermission):
    """
    Для Games/News/Vlogs и подобного контента: через API доступно только чтение.
    Создание/редактирование — через стандартную Django-админку владельцем/суперюзером.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS