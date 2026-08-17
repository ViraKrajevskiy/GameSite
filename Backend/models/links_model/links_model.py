from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from Backend.models.base_user_model.base_model import TimeManager


class ContentLink(TimeManager):
    """
    Ссылка, прикреплённая к чему угодно: новости, влогу, продукту.

    Раньше ссылку можно было только вписать в текст, и она оставалась
    неактивной строкой — по ней нельзя было кликнуть. Отдельные поля url
    у каждой модели проблему не решали: ссылка всегда одна.

    Generic-связь вместо трёх одинаковых моделей: поля, админка и вывод
    на фронте получаются одни на все разделы.
    """

    KIND_CHOICES = [
        ('auto', 'Определить по ссылке'),
        ('image', 'Картинка'),
        ('video', 'Видеофайл'),
        ('embed', 'Видео с YouTube / Vimeo'),
        ('file', 'Файл для скачивания'),
        ('page', 'Обычная ссылка'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    url = models.URLField('Ссылка', max_length=500)
    title = models.CharField(
        'Подпись (RU)', max_length=120, blank=True, default='',
        help_text='Не обязательно. Пусто — подписью станет адрес сайта.',
    )
    title_en = models.CharField(
        'Подпись (EN)', max_length=120, blank=True, default='',
        help_text='Не обязательно. Если пусто — покажется русская подпись.',
    )
    kind = models.CharField(
        'Как показывать', max_length=10, choices=KIND_CHOICES, default='auto',
        help_text='По умолчанию тип определяется по самой ссылке: картинка — '
                  'покажется картинкой, YouTube — встроенным плеером, архив — '
                  'кнопкой скачивания. Меняй, только если угадало неверно.',
    )
    order = models.PositiveSmallIntegerField(
        'Порядок', default=0,
        help_text='Меньше — выше в списке.',
    )

    class Meta:
        ordering = ['order', 'id']
        indexes = [models.Index(fields=['content_type', 'object_id'])]
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return self.title or self.url
