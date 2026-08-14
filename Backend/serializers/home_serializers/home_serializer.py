from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from Backend.models.home_model.home_model import HomeHero


def _pick(obj, field, lang):
    """Берёт поле нужного языка, а если оно пустое — откатывается на русское."""
    value = getattr(obj, f'{field}_{lang}', '') or ''
    if not value and lang != 'ru':
        value = getattr(obj, f'{field}_ru', '') or ''
    return value


def build_hero(hero, lang, request=None):
    """Собирает первый экран в том виде, в каком его ждёт главная страница."""
    image_url = ''
    if hero.art_image:
        image_url = hero.art_image.url
        if request is not None:
            image_url = request.build_absolute_uri(image_url)

    return {
        'showBadge': hero.show_badge,
        'badge': _pick(hero, 'badge', lang),

        'titleLines': [line.strip() for line in _pick(hero, 'title', lang).splitlines() if line.strip()],
        'titleAccent': _pick(hero, 'title_accent', lang),

        'showDeck': hero.show_deck,
        'deck': _pick(hero, 'deck', lang),

        'showBtn1': hero.show_btn1,
        'btn1Text': _pick(hero, 'btn1_text', lang),
        'btn1Url': hero.btn1_url,

        'showBtn2': hero.show_btn2,
        'btn2Text': _pick(hero, 'btn2_text', lang),
        'btn2Url': hero.btn2_url,

        'showStats': hero.show_stats,
        'stats': [
            {'num': stat.num, 'lab': _pick(stat, 'label', lang)}
            for stat in hero.stats.all()
        ],

        'showArt': hero.show_art,
        'artImage': image_url,
        'artTitle': _pick(hero, 'art_title', lang),
        'artUrl': hero.art_url,

        'showScore': hero.show_score,
        'score': hero.score,
        'scoreLabel': _pick(hero, 'score_label', lang),
    }


class HeroLangSerializer(serializers.Serializer):
    """
    Форма первого экрана для одного языка — то, что возвращает build_hero.

    Существует ради схемы: drf-spectacular не выводит тип из
    SerializerMethodField, и без неё ru/en попадали в OpenAPI как строки,
    хотя на деле это объекты.
    """
    showBadge = serializers.BooleanField()
    badge = serializers.CharField(allow_blank=True)

    titleLines = serializers.ListField(child=serializers.CharField())
    titleAccent = serializers.CharField(allow_blank=True)

    showDeck = serializers.BooleanField()
    deck = serializers.CharField(allow_blank=True)

    showBtn1 = serializers.BooleanField()
    btn1Text = serializers.CharField(allow_blank=True)
    btn1Url = serializers.CharField(allow_blank=True)

    showBtn2 = serializers.BooleanField()
    btn2Text = serializers.CharField(allow_blank=True)
    btn2Url = serializers.CharField(allow_blank=True)

    showStats = serializers.BooleanField()
    stats = serializers.ListField(child=serializers.DictField())

    showArt = serializers.BooleanField()
    artImage = serializers.CharField(allow_blank=True)
    artTitle = serializers.CharField(allow_blank=True)
    artUrl = serializers.CharField(allow_blank=True)

    showScore = serializers.BooleanField()
    score = serializers.IntegerField(allow_null=True)
    scoreLabel = serializers.CharField(allow_blank=True)


class HomeHeroSerializer(serializers.ModelSerializer):
    """Отдаёт первый экран сразу на двух языках: {"ru": {...}, "en": {...}}."""

    ru = serializers.SerializerMethodField()
    en = serializers.SerializerMethodField()

    class Meta:
        model = HomeHero
        fields = ['ru', 'en', 'updated_at']

    @extend_schema_field(HeroLangSerializer)
    def get_ru(self, obj):
        return build_hero(obj, 'ru', self.context.get('request'))

    @extend_schema_field(HeroLangSerializer)
    def get_en(self, obj):
        return build_hero(obj, 'en', self.context.get('request'))
