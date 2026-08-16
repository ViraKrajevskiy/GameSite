from django.db import models
from django.utils.text import slugify

from Backend.models.base_user_model.base_model import TimeManager, User


def unique_slug(model, title, instance=None):
    """Адрес из заголовка. Если такой уже занят — добавляем номер."""
    base = slugify(title or '', allow_unicode=True) or 'item'
    slug = base
    queryset = model.objects.all()
    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    i = 2
    while queryset.filter(slug=slug).exists():
        slug = f'{base}-{i}'
        i += 1
    return slug


class News(TimeManager):
    """
    Новость. Обязателен только заголовок — всё остальное можно дописать позже.
    Адрес (slug) генерируется из заголовка сам, если его не задали.
    """

    title = models.CharField('Заголовок', max_length=230)
    content = models.TextField('Текст', blank=True, default='')
    url = models.URLField('Ссылка', max_length=230, blank=True, default='')
    media = models.FileField(
        'Картинка или видео', upload_to='news/', blank=True, null=True,
        help_text='Не обязательно. Без файла карточка покажет узор с первой буквой заголовка.',
    )

    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='news',
        null=True, blank=True, verbose_name='Автор',
    )
    is_published = models.BooleanField('Опубликовано', default=False)
    slug = models.SlugField(
        'Адрес', max_length=255, unique=True, blank=True,
        help_text='Можно не заполнять — соберётся из заголовка.',
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(News, self.title, self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} {self.created_at}'
