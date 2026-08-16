from django.db.models import Avg
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from Backend.models.games_model.games_model import Games
from Backend.validators.file_validators.file_validators import validate_image_file


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


class GamesSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    platforms = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    # Обложка: только картинка до 5 МБ
    image = serializers.ImageField(required=False, validators=[validate_image_file])

    class Meta:
        model = Games
        fields = [
            'id', 'title', 'kind', 'kind_display', 'description', 'image', 'url',
            'platforms', 'average_rating', 'ratings_count', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            # Игра без обложки — рабочий случай. Пока image был обязательным,
            # создать игру можно было только multipart-запросом с файлом.
            'image': {'required': False},
            'url': {'required': False},
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
