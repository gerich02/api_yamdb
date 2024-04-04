import string
import random
from functools import lru_cache

from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .filters import FilterTitleSet
from .mixins import CategoryGenreMixin
from .permissions import (
    IsAdminOnlyPermission,
    IsAdminOrReadOnlyPermission,
    IsAuthorModeratorAdminOrReadOnlyPermission,
    SelfEditUserOnlyPermission
)
from .serializers import (
    CategorySerializer,
    CreateUserSerializer,
    CommentSerializer,
    GenreSerializer,
    TokenSerializer,
    UsersSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    SelfSerializer
)
from api_yamdb.settings import EMAIL_HOST_USER
from reviews.models import Category, Genre, Review, Title, User


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitleSet
    http_method_names = ['get', 'patch', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update',):
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnlyPermission,)
    http_method_names = ['get', 'patch', 'post', 'delete']

    @lru_cache(maxsize=None)
    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnlyPermission,)
    http_method_names = ['get', 'patch', 'post', 'delete']

    @lru_cache(maxsize=None)
    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class UserCreate(APIView):
    """Получение кода подтверждения на переданный email."""
    permission_classes = (AllowAny,)

    random_code = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=10))

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if (User.objects.filter(username=request.data.get('username'),
                                email=request.data.get('email'))):
            user = User.objects.get(
                username=request.data.get('username'))
            serializer = CreateUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(confirmation_code=self.random_code)
        user = User.objects.get(username=request.data.get('username'))
        send_mail(
            subject='Код подтверждения для доступа к API YaMDb.',
            message=(
                f'Ваш код подтверждения: {user.confirmation_code}\n'
            ),
            from_email=EMAIL_HOST_USER,
            recipient_list=[request.data.get('email')],
            fail_silently=False,
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )


class UserGetToken(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=request.data.get('username')
        )
        print(user)
        if str(user.confirmation_code) == request.data.get(
            'confirmation_code'
        ):
            refresh = RefreshToken.for_user(user)
            token = {'token': str(refresh.access_token)}
            return Response(
                token, status=HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения.'},
            status=HTTP_400_BAD_REQUEST
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdminOnlyPermission,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=['get', 'patch'], detail=False,
        url_path='me', permission_classes=(SelfEditUserOnlyPermission,)
    )
    def me_user(self, request):
        if request.method == 'GET':
            user = get_object_or_404(
                User, username=request.user
            )
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        user = get_object_or_404(
            User, username=request.user
        )
        serializer = SelfSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)
