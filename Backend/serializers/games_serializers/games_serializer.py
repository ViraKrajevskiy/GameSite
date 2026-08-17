from django.db.models import Avg
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from Backend.models.games_model.games_model import Games, GameVersion
from Backend.validators.file_validators.file_validators import validate_image_file
from Backend.serializers.links_serializers.links_serializer import ContentLinkSerializer


class GamePlatformSerializer(serializers.Serializer):
    """
    Форма одного элемента из get_platforms.

    Нужна только для схемы: drf-spectacular не умеет вывести тип из
    SerializerMethodField, который собирает словари вручную, и без неё
    поле уходило в OpenAPI как обычная строка.
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    icon = serializers.CharField(allow_null=True)
    image = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    status_display = serializers.CharField()
    url = serializers.CharField(allow_null=True)
    release_date = serializers.DateField(allow_null=True)


class GameVersionSerializer(serializers.ModelSerializer):
    """История обновлений продукта. Только чтение: версии заводятся в админке."""

    class Meta:
        model = GameVersion
        fields = ['id', 'number', 'released_at', 'changelog', 'changelog_en', 'url']


class GamesSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    platforms = serializers.SerializerMethodField()
    versions = GameVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()
    links = ContentLinkSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    # Обложка: только картинка до 5 МБ
    image = serializers.ImageField(required=False, validators=[validate_image_file])

    class Meta:
        model = Games
        fields = [
            'id', 'title', 'title_en', 'kind', 'kind_display',
            'description', 'description_en', 'image', 'url',
            'platforms', 'versions', 'latest_version', 'links',
            'average_rating', 'ratings_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            # Игра без обложки — рабочий случай. Пока image был обязательным,
            # создать игру можно было только multipart-запросом с файлом.
            'image': {'required': False},
            'url': {'required': False},
            # Английская версия не обязательна: где пусто — фронт покажет русский
            'title_en': {'required': False, 'allow_blank': True},
            'description_en': {'required': False, 'allow_blank': True},
        }

    @extend_schema_field(GamePlatformSerializer(many=True))
    def get_platforms(self, obj):
        """
        Платформы вместе со статусом релиза и ссылкой на скачивание —
        всё это уже лежало в GamePlatformRelease, просто не отдавалось наружу.
        """
        request = self.context.get('request')
        result = []

        for release in obj.platform_releases.all():
            platform = release.platform
            image = None
            if platform.image:
                image = platform.image.url
                if request is not None:
                    image = request.build_absolute_uri(image)

            result.append({
                'id': platform.id,
                'title': platform.title,
                'icon': platform.icon,
                'image': image,
                'status': release.status,
                'status_display': release.get_status_display(),
                'url': release.url_platform,
                'release_date': release.release_date,
            })

        return result

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_average_rating(self, obj):
        avg = getattr(obj, 'avg_rating', None)
        if avg is None:
            agg = obj.ratings.aggregate(avg=Avg('rating'))
            avg = agg['avg']
        return round(avg, 1) if avg is not None else None

    @extend_schema_field(serializers.IntegerField())
    def get_ratings_count(self, obj):
        count = getattr(obj, 'ratings_count', None)
        if count is None:
            count = obj.ratings.count()
        return count

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_latest_version(self, obj):
        """
        Номер свежей версии — чтобы карточка показала плашку «v1.2»,
        не разбирая на фронте весь список.

        Порядок задан в Meta.ordering модели, первый элемент и есть свежий.
        Обращаемся через срез списка, а не .first(): queryset уже
        прогружен prefetch_related, лишний запрос в базу не нужен.
        """
        versions = list(obj.versions.all()[:1])
        return versions[0].number if versions else None
