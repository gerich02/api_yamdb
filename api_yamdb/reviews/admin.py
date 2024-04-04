from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'Тут ничего нет'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('review__title',)
    list_filter = ('review__title',)
    empty_value_display = 'Тут ничего нет'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('review', 'author')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'score',
    )
    search_fields = ('title', "author__username")
    list_filter = ('pub_date',)
    empty_value_display = 'Тут ничего нет'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'description',
    )
    search_fields = ('name', 'category__name')
    list_filter = ('category__name',)
    empty_value_display = 'Тут ничего нет'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'Тут ничего нет'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = 'Тут ничего нет'
