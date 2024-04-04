from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet

from .permissions import IsAdminOrReadOnlyPermission


class CategoryGenreMixin(
    GenericViewSet,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
):
    permission_classes: tuple = (IsAdminOrReadOnlyPermission,)
    filter_backends: tuple = (DjangoFilterBackend, SearchFilter)
    search_fields: tuple = ('name', 'slug',)
    lookup_field: str = 'slug'
