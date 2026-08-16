from django.utils.text import slugify
from rest_framework import serializers

from Backend.models.vlogs_model.vlogs_model import Vlogs
from Backend.validators.file_validators.file_validators import validate_media_file


class VlogsSerializer(serializers.ModelSerializer):
    # Наружу отдаём короткие имена, внутри — поля модели.
    # Раньше все три были read_only, из-за чего влог физически нельзя было
    # создать через API: передавать было нечего.
    title = serializers.CharField(source='vlog_title')
    description = serializers.CharField(source='text', required=False, allow_blank=True)
    embed_url = serializers.URLField(source='url', required=False, allow_blank=True)
    author = serializers.StringRelatedField(read_only=True)
    media = serializers.FileField(required=False, validators=[validate_media_file])

    class Meta:
        model = Vlogs
        fields = [
            'id', 'title', 'description', 'embed_url', 'media',
            'author', 'is_published', 'slug', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']
        extra_kwargs = {
            'slug': {'required': False},
            'media': {'required': False},
        }

    def validate(self, attrs):
        if not attrs.get('slug') and attrs.get('vlog_title'):
            attrs['slug'] = _unique_slug(Vlogs, attrs['vlog_title'])
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
