from django.utils.text import slugify
from rest_framework import serializers

from Backend.models.news_model.news_model import News
from Backend.validators.file_validators.file_validators import validate_media_file


class NewsSerializer(serializers.ModelSerializer):
    # Автора подставляет вьюсет из request.user — из тела его брать нельзя,
    # иначе можно опубликовать новость от чужого имени.
    author = serializers.StringRelatedField(read_only=True)
    # Картинка или видео до 50 МБ; исполняемые форматы отсекаются
    media = serializers.FileField(required=False, validators=[validate_media_file])

    class Meta:
        model = News
        fields = [
            'id', 'title', 'title_en', 'content', 'content_en', 'url', 'media',
            'author', 'is_published', 'slug', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']
        extra_kwargs = {
            # slug генерируем из заголовка, если не прислали
            'slug': {'required': False, 'allow_blank': True},
            'content': {'required': False, 'allow_blank': True},
            # Английская версия не обязательна: где пусто — фронт покажет русский
            'title_en': {'required': False, 'allow_blank': True},
            'content_en': {'required': False, 'allow_blank': True},
            # Новость без файла — нормальный случай; иначе создать её
            # можно было бы только multipart-запросом с вложением.
            'media': {'required': False},
            'url': {'required': False},
        }

    def validate(self, attrs):
        if not attrs.get('slug') and attrs.get('title'):
            attrs['slug'] = _unique_slug(News, attrs['title'])
        return attrs


def _unique_slug(model, title):
    """slug из заголовка + числовой суффикс, если такой уже занят."""
    base = slugify(title, allow_unicode=True) or 'item'
    slug = base
    i = 2
    while model.objects.filter(slug=slug).exists():
        slug = f'{base}-{i}'
        i += 1
    return slug
