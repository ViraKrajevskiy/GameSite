from django.db import models

from Backend.models.base_user_model.base_model import TimeManager, User
from Backend.models.news_model.news_model import unique_slug


class Vlogs(TimeManager):
    """
    Влог. Обязателен только заголовок: видео можно приложить файлом,
    дать ссылкой на YouTube/Vimeo или не давать вовсе.
    """

    author = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Автор',
    )
    vlog_title = models.CharField('Заголовок', max_length=500)
    text = models.TextField('Описание', blank=True, default='')

    url = models.URLField(
        'Ссылка на видео', max_length=230, blank=True, default='',
        help_text='YouTube и Vimeo встраиваются плеером, остальные — кнопкой «смотреть».',
    )
    media = models.FileField(
        'Картинка или видеофайл', upload_to='vlogs/', blank=True, null=True,
        help_text='Не обязательно. Без файла карточка покажет узор с первой буквой заголовка.',
    )
    is_published = models.BooleanField('Опубликовано', default=False)
    slug = models.SlugField(
        'Адрес', max_length=255, unique=True, blank=True,
        help_text='Можно не заполнять — соберётся из заголовка.',
    )

    class Meta:
        verbose_name = 'Влог'
        verbose_name_plural = 'Влоги'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Vlogs, self.vlog_title, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.vlog_title}, {self.created_at}'
