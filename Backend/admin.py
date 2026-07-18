from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from Backend.models.base_user_model.base_model import User
from Backend.models.news_model.news_model import News
from Backend.models.comments_model.news_coment import NewsComment
from Backend.models.vlogs_model.vlogs_model import Vlogs
from Backend.models.comments_model.vlogs_coment import VlogsComment
from Backend.models.games_model.games_model import Games, Platform, GamePlatformRelease
from Backend.models.games_model.game_rating_models import GamesRating


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ['email']
    list_display = ['email', 'username', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Профиль', {'fields': ('avatar', 'bio', 'role')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


class GamePlatformReleaseInline(admin.TabularInline):
    model = GamePlatformRelease
    extra = 1


@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    inlines = [GamePlatformReleaseInline]


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(GamePlatformRelease)
class GamePlatformReleaseAdmin(admin.ModelAdmin):
    list_display = ['game', 'platform', 'status', 'release_date']
    list_filter = ['status', 'platform']
    search_fields = ['game__title', 'platform__title']


@admin.register(GamesRating)
class GamesRatingAdmin(admin.ModelAdmin):
    list_display = ['game', 'rating_writer', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['game__title', 'rating_writer__username']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'author__username']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ['news', 'comment_writer', 'text', 'created_at']
    search_fields = ['text', 'comment_writer__username']
    actions = ['delete_selected']


@admin.register(Vlogs)
class VlogsAdmin(admin.ModelAdmin):
    list_display = ['vlog_title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['vlog_title', 'author__username']
    prepopulated_fields = {'slug': ('vlog_title',)}


@admin.register(VlogsComment)
class VlogsCommentAdmin(admin.ModelAdmin):
    list_display = ['vlogs', 'vl_comment_author', 'comment', 'created_at']
    search_fields = ['comment', 'vl_comment_author__username']
    actions = ['delete_selected']