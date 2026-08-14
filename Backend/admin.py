from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from Backend.models.base_user_model.base_model import User
from Backend.models.news_model.news_model import News
from Backend.models.comments_model.news_coment import NewsComment
from Backend.models.vlogs_model.vlogs_model import Vlogs
from Backend.models.comments_model.vlogs_coment import VlogsComment
from Backend.models.games_model.games_model import Games, Platform, GamePlatformRelease
from Backend.models.games_model.game_rating_models import GamesRating
from Backend.models.home_model.home_model import HomeHero, HeroStat
from Backend.models.resume_model.resume_model import (
    Resume, ResumeContact, ResumeFact, ResumeSkillGroup, ResumeExperience,
    ResumeProject, ResumeProjectLink, ResumeEducation, ResumeLanguage,
)


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
    fields = ['platform', 'status', 'url_platform', 'release_date']
    autocomplete_fields = ['platform']
    verbose_name = 'Платформа'
    verbose_name_plural = 'На каких платформах доступно'


@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ['title', 'kind', 'platform_list', 'created_at']
    list_filter = ['kind']
    search_fields = ['title']
    inlines = [GamePlatformReleaseInline]
    fields = ['title', 'kind', 'description', 'image', 'url']

    @admin.display(description='Платформы')
    def platform_list(self, obj):
        titles = [release.platform.title for release in obj.platform_releases.all()]
        return ', '.join(titles) if titles else '—'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('platform_releases__platform')


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon']
    list_filter = ['icon']
    list_editable = ['icon']
    search_fields = ['title']
    fields = ['title', 'icon', 'image']


@admin.register(GamePlatformRelease)
class GamePlatformReleaseAdmin(admin.ModelAdmin):
    list_display = ['game', 'platform', 'status', 'release_date']
    list_filter = ['status', 'platform']
    search_fields = ['game__title', 'platform__title']
    autocomplete_fields = ['game', 'platform']


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


# --- РЕЗЮМЕ (страница «О нас») ---

class ResumeContactInline(admin.TabularInline):
    model = ResumeContact
    extra = 1
    fields = ['order', 'label_ru', 'label_en', 'value', 'url']
    ordering = ['order', 'id']


class ResumeFactInline(admin.TabularInline):
    model = ResumeFact
    extra = 1
    fields = ['order', 'num', 'label_ru', 'label_en']
    ordering = ['order', 'id']


class ResumeSkillGroupInline(admin.TabularInline):
    model = ResumeSkillGroup
    extra = 1
    fields = ['order', 'title_ru', 'title_en', 'items']
    ordering = ['order', 'id']


class ResumeExperienceInline(admin.StackedInline):
    model = ResumeExperience
    extra = 0
    fields = [
        'order',
        ('period_ru', 'period_en'),
        ('company', 'place_ru', 'place_en'),
        ('title_ru', 'title_en'),
        'points_ru', 'points_en',
        'stack',
    ]
    ordering = ['order', 'id']


class ResumeEducationInline(admin.TabularInline):
    model = ResumeEducation
    extra = 1
    fields = ['order', 'year', 'place', 'detail_ru', 'detail_en']
    ordering = ['order', 'id']


class ResumeLanguageInline(admin.TabularInline):
    model = ResumeLanguage
    extra = 1
    fields = ['order', 'name_ru', 'name_en', 'level_ru', 'level_en']
    ordering = ['order', 'id']


class ResumeProjectLinkInline(admin.TabularInline):
    model = ResumeProjectLink
    extra = 1
    fields = ['order', 'label_ru', 'label_en', 'url']
    ordering = ['order', 'id']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['name_ru', 'role_ru', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name_ru', 'name_en', 'role_ru']
    readonly_fields = ['created_at', 'updated_at']
    save_on_top = True
    inlines = [
        ResumeContactInline,
        ResumeFactInline,
        ResumeSkillGroupInline,
        ResumeExperienceInline,
        ResumeEducationInline,
        ResumeLanguageInline,
    ]
    fieldsets = (
        ('Главное', {
            'fields': (
                'is_active',
                ('name_ru', 'name_en'),
                ('role_ru', 'role_en'),
                ('tagline_ru', 'tagline_en'),
            ),
        }),
        ('Обо мне', {
            'description': 'Каждый абзац — с новой строки.',
            'fields': ('about_ru', 'about_en'),
        }),
        ('Блок «Открыт к работе»', {
            'fields': (
                ('cta_title_ru', 'cta_title_en'),
                ('cta_text_ru', 'cta_text_en'),
                ('cta_btn1_text_ru', 'cta_btn1_text_en', 'cta_btn1_url'),
                ('cta_btn2_text_ru', 'cta_btn2_text_en', 'cta_btn2_url'),
            ),
        }),
        ('Заголовки разделов', {
            'classes': ('collapse',),
            'description': 'Можно не трогать — уже заполнены по умолчанию.',
            'fields': (
                ('eyebrow_ru', 'eyebrow_en'),
                ('contacts_title_ru', 'contacts_title_en'),
                ('facts_title_ru', 'facts_title_en'),
                ('about_title_ru', 'about_title_en'),
                ('stack_title_ru', 'stack_title_en'),
                ('exp_title_ru', 'exp_title_en'),
                ('proj_title_ru', 'proj_title_en'),
                ('edu_title_ru', 'edu_title_en'),
                ('lang_title_ru', 'lang_title_en'),
            ),
        }),
        ('Служебное', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ResumeProject)
class ResumeProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'kind_ru', 'resume', 'order']
    list_editable = ['order']
    search_fields = ['name']
    inlines = [ResumeProjectLinkInline]
    fields = [
        'resume', 'order', 'name',
        ('kind_ru', 'kind_en'),
        'description_ru', 'description_en',
    ]


# --- ГЛАВНАЯ: ПЕРВЫЙ ЭКРАН ---

class HeroStatInline(admin.TabularInline):
    model = HeroStat
    extra = 1
    fields = ['order', 'num', 'label_ru', 'label_en']
    ordering = ['order', 'id']


@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active', 'show_art', 'updated_at']
    list_filter = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    save_on_top = True
    inlines = [HeroStatInline]
    fieldsets = (
        ('Заголовок', {
            'fields': (
                'is_active',
                ('show_badge', 'badge_ru', 'badge_en'),
                ('title_ru', 'title_en'),
                ('title_accent_ru', 'title_accent_en'),
            ),
        }),
        ('Описание', {
            'fields': ('show_deck', ('deck_ru', 'deck_en')),
        }),
        ('Кнопки', {
            'fields': (
                ('show_btn1', 'btn1_text_ru', 'btn1_text_en', 'btn1_url'),
                ('show_btn2', 'btn2_text_ru', 'btn2_text_en', 'btn2_url'),
            ),
        }),
        ('Цифры', {
            'description': 'Сами цифры добавляются в таблице внизу страницы.',
            'fields': ('show_stats',),
        }),
        ('Блок с картинкой справа', {
            'fields': (
                'show_art',
                'art_image',
                ('art_title_ru', 'art_title_en'),
                'art_url',
                ('show_score', 'score', 'score_label_ru', 'score_label_en'),
            ),
        }),
        ('Служебное', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
