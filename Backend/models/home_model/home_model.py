from django.db import models

from Backend.models.base_user_model.base_model import TimeManager


class HomeHero(TimeManager):
    """
    Первый экран главной страницы (большой заголовок, кнопки, цифры и картинка справа).

    Заполняется через админку. Активным считается блок с is_active=True
    (берётся самый свежий). Любой элемент можно спрятать галочкой «Показывать…».
    """

    # --- жёлтый ярлык над заголовком ---
    show_badge = models.BooleanField('Показывать ярлык', default=True)
    badge_ru = models.CharField('Ярлык (RU)', max_length=120, blank=True, default='⚠ Только жёсткие игры')
    badge_en = models.CharField('Ярлык (EN)', max_length=120, blank=True, default='⚠ Hardcore games only')

    # --- заголовок ---
    title_ru = models.TextField(
        'Заголовок (RU)', blank=True, default='Без\nпощады.',
        help_text='Каждая строка — с новой строки. Последняя, красная строка — в поле ниже.',
    )
    title_en = models.TextField('Заголовок (EN)', blank=True, default='No\nmercy.')
    title_accent_ru = models.CharField(
        'Красная строка заголовка (RU)', max_length=120, blank=True, default='Только игры.',
    )
    title_accent_en = models.CharField(
        'Красная строка заголовка (EN)', max_length=120, blank=True, default='Just games.',
    )

    # --- абзац под заголовком ---
    show_deck = models.BooleanField('Показывать описание', default=True)
    deck_ru = models.TextField('Описание (RU)', blank=True)
    deck_en = models.TextField('Описание (EN)', blank=True)

    # --- кнопки ---
    show_btn1 = models.BooleanField('Показывать кнопку 1', default=True)
    btn1_text_ru = models.CharField('Кнопка 1: текст (RU)', max_length=80, blank=True, default='Открыть каталог →')
    btn1_text_en = models.CharField('Кнопка 1: текст (EN)', max_length=80, blank=True, default='Open catalog →')
    btn1_url = models.CharField('Кнопка 1: ссылка', max_length=300, blank=True, default='/games')

    show_btn2 = models.BooleanField('Показывать кнопку 2', default=True)
    btn2_text_ru = models.CharField('Кнопка 2: текст (RU)', max_length=80, blank=True, default='Читать новости')
    btn2_text_en = models.CharField('Кнопка 2: текст (EN)', max_length=80, blank=True, default='Read the news')
    btn2_url = models.CharField('Кнопка 2: ссылка', max_length=300, blank=True, default='/news')

    # --- полоска с цифрами ---
    show_stats = models.BooleanField('Показывать цифры', default=True)

    # --- блок с картинкой справа ---
    show_art = models.BooleanField(
        'Показывать блок справа', default=True,
        help_text='Если снять галочку — текст займёт всю ширину экрана.',
    )
    art_image = models.ImageField(
        'Картинка / логотип', upload_to='hero/', blank=True, null=True,
        help_text='Если не загружать — останется фирменный узор с названием.',
    )
    art_title_ru = models.CharField('Подпись на картинке (RU)', max_length=120, blank=True)
    art_title_en = models.CharField('Подпись на картинке (EN)', max_length=120, blank=True)
    art_url = models.CharField(
        'Ссылка с картинки', max_length=300, blank=True,
        help_text='Куда ведёт клик по блоку. Пусто — блок не кликабельный.',
    )

    show_score = models.BooleanField('Показывать оценку', default=True)
    score = models.CharField('Оценка', max_length=10, blank=True, default='9.4')
    score_label_ru = models.CharField('Подпись к оценке (RU)', max_length=40, blank=True, default='из 10')
    score_label_en = models.CharField('Подпись к оценке (EN)', max_length=40, blank=True, default='out of 10')

    is_active = models.BooleanField(
        'Показывать на сайте', default=True,
        help_text='Если активных несколько — берётся последний изменённый.',
    )

    class Meta:
        verbose_name = 'Главная: первый экран'
        verbose_name_plural = 'Главная: первый экран'
        ordering = ['-updated_at']

    def __str__(self):
        first_line = (self.title_ru or '').splitlines()
        return f'Первый экран: {first_line[0] if first_line else "без заголовка"}'


class HeroStat(TimeManager):
    """Одна цифра в полоске под кнопками (например «340+ игр в базе»)."""

    hero = models.ForeignKey(HomeHero, on_delete=models.CASCADE, related_name='stats')
    order = models.PositiveIntegerField('Порядок', default=0)
    num = models.CharField('Цифра', max_length=20)
    label_ru = models.CharField('Подпись (RU)', max_length=80)
    label_en = models.CharField('Подпись (EN)', max_length=80, blank=True)

    class Meta:
        verbose_name = 'Цифра'
        verbose_name_plural = 'Цифры'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.num} {self.label_ru}'
