from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOnlyPermission(BasePermission):
    """
    Проверяет, является ли пользователь администратором.
    """
    message: str = 'Доступно только администраторам'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class SelfEditUserOnlyPermission(BasePermission):
    """
    Проверяет, может ли пользователь редактировать
    только свои собственные посты.
    """
    message: str = 'Вы не можете редактировать чужие посты!'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user


class IsAdminOrReadOnlyPermission(BasePermission):
    """
    Проверяет, является ли пользователь администратором
    или разрешены только методы чтения.
    """
    message: str = 'Доступно только администраторам'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser)
            )
        )


class IsAuthorModeratorAdminOrReadOnlyPermission(BasePermission):
    """
    Проверяет, имеет ли пользователь права на доступ или редактирование объекта
    в зависимости от его роли (автор, модератор, администратор) или разрешены
    только методы чтения.
    """
    message: str = 'Доступно только модераторам или администраторам'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user or request.user.is_moderator
            or request.user.is_admin or request.user.is_superuser
        )
