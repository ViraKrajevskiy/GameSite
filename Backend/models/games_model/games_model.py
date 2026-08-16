from django.db import models
from Backend.models.base_user_model.base_model import TimeManager


class Games(TimeManager):
    """Продукт: игра, десктопная программа, веб- или мобильное приложение."""

    KIND_CHOICES = [
        ('game', 'Игра'),
        ('desktop', 'Десктопная программа'),
        ('web', 'Веб-приложение'),
        ('mobile', 'Мобильное приложение'),
        ('other', 'Другое'),
    ]

    title = models.CharField('Название (RU)', max_length=100)
    title_en = models.CharField('Название (EN)', max_length=100, blank=True, default='', help_text='Не обязательно. Если пусто — на английской версии покажется русский текст.')
    kind = models.CharField(
        'Тип продукта', max_length=20, choices=KIND_CHOICES, default='game',
        help_text='Показывается плашкой на карточке и даёт фильтр в каталоге.',
    )
    description = models.TextField('Описание (RU)', blank=True, default='')
    description_en = models.TextField('Описание (EN)', blank=True, default='', help_text='Не обязательно. Если пусто — на английской версии покажется русский текст.')
    image = models.ImageField(
        'Обложка', upload_to='images/', blank=True, null=True,
        help_text='Не обязательно. Без обложки карточка покажет узор с первой буквой названия.',
    )
    url = models.URLField('Основная ссылка', blank=True, default='')
    platforms = models.ManyToManyField('Platform', through='GamePlatformRelease', related_name='games')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.title} ({self.get_kind_display()})' 


class Platform(TimeManager):
    """Платформа: Windows, Linux, macOS, Web, PlayStation, Android и т.д."""

    ICON_CHOICES = [
        ('windows', 'Windows'),
        ('linux', 'Linux'),
        ('macos', 'macOS'),
        ('web', 'Веб / браузер'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('playstation', 'PlayStation'),
        ('xbox', 'Xbox'),
        ('nintendo', 'Nintendo'),
        ('steam', 'Steam'),
        ('itch', 'itch.io'),
        ('other', 'Без значка'),
    ]

    title = models.CharField('Название', max_length=100)
    icon = models.CharField(
        'Значок', max_length=20, choices=ICON_CHOICES, default='other',
        help_text='Какой значок рисовать на карточке продукта.',
    )
    image = models.ImageField('Своя картинка', upload_to='images/', blank=True, null=True)

    class Meta:
        verbose_name = 'Платформа'
        verbose_name_plural = 'Платформы'

    def __str__(self):
        return self.title


class GamePlatformRelease(TimeManager):
    STATUS_CHOICES = [
        ('not_released', 'Не выпущено'),
        ('in_dev', 'В разработке'),
        ('beta', 'Бета'),
        ('waiting', 'Скоро'),
        ('released', 'Вышло'),
    ]

    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name='platform_releases')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='game_releases')
    url_platform = models.URLField('Ссылка на скачивание', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='not_released')
    release_date = models.DateField('Дата выхода', null=True, blank=True)

    class Meta:
        unique_together = ('game', 'platform')
        verbose_name = 'Платформа продукта'
        verbose_name_plural = 'Платформы продукта'

    def __str__(self):
        return f'{self.game.title} — {self.platform.title} ({self.status})'