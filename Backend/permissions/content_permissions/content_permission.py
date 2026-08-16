from rest_framework import permissions

from Backend.permissions.moderator_permissions.moderator_permission import IsAdminOrModerator


class ContentPermission(permissions.BasePermission):
    """
    Для контента: Games / News / Vlogs.

    Раньше здесь стоял ReadOnlyForEveryone — через API нельзя было создать
    ничего вообще, даже суперюзеру, а роль 'creator' («Создатель контента»)
    существовала в модели, но не давала никаких прав: метод is_creator()
    не использовался ни в одном пермишене.

    Правила:
      - Читать (GET/HEAD/OPTIONS) может любой, в том числе анонимный.
      - Создавать (POST) может создатель контента или админ.
      - Редактировать (PUT/PATCH) может админ — любое, создатель — только своё.
      - Удалять (DELETE) может админ и модератор — любое (это модерация),
        создатель — только своё.

    «Своё» определяется по полю author у объекта. У Games автора нет — это
    общий каталог, поэтому там правка доступна любому создателю контента.
    """

    def _can_write(self, user):
        return bool(
            user
            and user.is_authenticated
            and (user.is_creator() or user.is_admin())
        )

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Удаление доступно ещё и модератору — дальше решает объектный уровень
        if request.method == 'DELETE' and IsAdminOrModerator.check(request.user):
            return True
        return self._can_write(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if user.is_authenticated and user.is_admin():
            return True

        # Модератор может убрать чужой материал, но не переписывать его
        if request.method == 'DELETE' and IsAdminOrModerator.check(user):
            return True

        author = getattr(obj, 'author', None)
        if author is None:
            # У модели нет владельца (Games) — общий каталог для создателей
            return self._can_write(user)

        return self._can_write(user) and author == user
