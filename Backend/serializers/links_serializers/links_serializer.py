from rest_framework import serializers

from Backend.models.links_model.links_model import ContentLink


class ContentLinkSerializer(serializers.ModelSerializer):
    """
    Ссылка, прикреплённая к материалу. Только чтение — заводятся в админке.

    kind отдаём как есть, включая 'auto': что показывать — картинку, плеер
    или кнопку — решает фронт по самому адресу. Держать распознавание
    в одном месте проще, чем синхронизировать два списка расширений.
    """

    class Meta:
        model = ContentLink
        fields = ['id', 'url', 'title', 'title_en', 'kind', 'order']
