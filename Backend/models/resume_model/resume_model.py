from django.db import models

from Backend.models.base_user_model.base_model import TimeManager


class Resume(TimeManager):
    """
    Резюме владельца сайта — то, что показывается на странице /about.

    Заполняется через админку. Активным считается резюме с is_active=True
    (берётся самое свежее). Все текстовые поля продублированы на русском
    и английском — сайт сам подставит нужный язык по переключателю RU/EN.
    """

    # --- основное ---
    name_ru = models.CharField('Имя (RU)', max_length=120)
    name_en = models.CharField('Имя (EN)', max_length=120, blank=True)

    role_ru = models.CharField('Должность (RU)', max_length=200)
    role_en = models.CharField('Должность (EN)', max_length=200, blank=True)

    tagline_ru = models.TextField('Короткое описание (RU)', blank=True)
    tagline_en = models.TextField('Короткое описание (EN)', blank=True)

    about_ru = models.TextField(
        'Обо мне (RU)', blank=True,
        help_text='Каждый абзац — с новой строки. Пустые строки игнорируются.',
    )
    about_en = models.TextField('Обо мне (EN)', blank=True)

    # --- блок «открыт к работе» ---
    cta_title_ru = models.CharField('CTA: заголовок (RU)', max_length=120, blank=True, default='Открыт к работе')
    cta_title_en = models.CharField('CTA: заголовок (EN)', max_length=120, blank=True, default='Open to work')
    cta_text_ru = models.TextField('CTA: текст (RU)', blank=True)
    cta_text_en = models.TextField('CTA: текст (EN)', blank=True)

    cta_btn1_text_ru = models.CharField('CTA: кнопка 1, текст (RU)', max_length=80, blank=True)
    cta_btn1_text_en = models.CharField('CTA: кнопка 1, текст (EN)', max_length=80, blank=True)
    cta_btn1_url = models.URLField('CTA: кнопка 1, ссылка', max_length=300, blank=True)

    cta_btn2_text_ru = models.CharField('CTA: кнопка 2, текст (RU)', max_length=80, blank=True)
    cta_btn2_text_en = models.CharField('CTA: кнопка 2, текст (EN)', max_length=80, blank=True)
    cta_btn2_url = models.URLField('CTA: кнопка 2, ссылка', max_length=300, blank=True)

    # --- заголовки разделов (можно не трогать) ---
    eyebrow_ru = models.CharField('Ярлык над именем (RU)', max_length=60, blank=True, default='Резюме')
    eyebrow_en = models.CharField('Ярлык над именем (EN)', max_length=60, blank=True, default='Résumé')
    contacts_title_ru = models.CharField('Заголовок «Контакты» (RU)', max_length=60, blank=True, default='Контакты')
    contacts_title_en = models.CharField('Заголовок «Контакты» (EN)', max_length=60, blank=True, default='Contacts')
    facts_title_ru = models.CharField('Заголовок «Коротко» (RU)', max_length=60, blank=True, default='Коротко')
    facts_title_en = models.CharField('Заголовок «Коротко» (EN)', max_length=60, blank=True, default='At a glance')
    about_title_ru = models.CharField('Заголовок «Обо мне» (RU)', max_length=60, blank=True, default='Обо мне')
    about_title_en = models.CharField('Заголовок «Обо мне» (EN)', max_length=60, blank=True, default='About me')
    stack_title_ru = models.CharField('Заголовок «Стек» (RU)', max_length=60, blank=True, default='Технический стек')
    stack_title_en = models.CharField('Заголовок «Стек» (EN)', max_length=60, blank=True, default='Tech stack')
    exp_title_ru = models.CharField('Заголовок «Опыт» (RU)', max_length=60, blank=True, default='Опыт работы')
    exp_title_en = models.CharField('Заголовок «Опыт» (EN)', max_length=60, blank=True, default='Experience')
    proj_title_ru = models.CharField('Заголовок «Проекты» (RU)', max_length=60, blank=True, default='Проекты')
    proj_title_en = models.CharField('Заголовок «Проекты» (EN)', max_length=60, blank=True, default='Projects')
    edu_title_ru = models.CharField('Заголовок «Образование» (RU)', max_length=60, blank=True, default='Образование')
    edu_title_en = models.CharField('Заголовок «Образование» (EN)', max_length=60, blank=True, default='Education')
    lang_title_ru = models.CharField('Заголовок «Языки» (RU)', max_length=60, blank=True, default='Языки')
    lang_title_en = models.CharField('Заголовок «Языки» (EN)', max_length=60, blank=True, default='Languages')

    is_active = models.BooleanField(
        'Показывать на сайте', default=True,
        help_text='Если активных несколько — берётся последнее изменённое.',
    )

    class Meta:
        verbose_name = 'Резюме'
        verbose_name_plural = 'Резюме'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name_ru} — {self.role_ru}'


class ResumeSection(TimeManager):
    """Общий предок для строк резюме: ссылка на резюме + порядок сортировки."""

    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        abstract = True
        ordering = ['order', 'id']


class ResumeContact(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='contacts')
    label_ru = models.CharField('Подпись (RU)', max_length=60)
    label_en = models.CharField('Подпись (EN)', max_length=60, blank=True)
    value = models.CharField('Значение', max_length=200, help_text='Что видно на сайте: @ник, почта, номер.')
    url = models.CharField('Ссылка', max_length=300, help_text='https://…, mailto:…, tel:…')

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.label_ru}: {self.value}'


class ResumeFact(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='facts')
    num = models.CharField('Цифра', max_length=20, help_text='Например: 1.5, 5+, 3')
    label_ru = models.CharField('Подпись (RU)', max_length=80)
    label_en = models.CharField('Подпись (EN)', max_length=80, blank=True)

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Цифра «коротко»'
        verbose_name_plural = 'Цифры «коротко»'

    def __str__(self):
        return f'{self.num} {self.label_ru}'


class ResumeSkillGroup(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skill_groups')
    title_ru = models.CharField('Группа (RU)', max_length=80)
    title_en = models.CharField('Группа (EN)', max_length=80, blank=True)
    items = models.TextField('Технологии', help_text='Через запятую: Python, Django, DRF')

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Группа навыков'
        verbose_name_plural = 'Технический стек'

    def __str__(self):
        return self.title_ru

    @property
    def items_list(self):
        return [item.strip() for item in self.items.split(',') if item.strip()]


class ResumeExperience(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience')
    period_ru = models.CharField('Период (RU)', max_length=80, help_text='Например: Июнь 2026 — Август 2026')
    period_en = models.CharField('Период (EN)', max_length=80, blank=True)
    company = models.CharField('Компания', max_length=120)
    place_ru = models.CharField('Город (RU)', max_length=80, blank=True)
    place_en = models.CharField('Город (EN)', max_length=80, blank=True)
    title_ru = models.CharField('Должность (RU)', max_length=200)
    title_en = models.CharField('Должность (EN)', max_length=200, blank=True)
    points_ru = models.TextField('Задачи (RU)', blank=True, help_text='Каждый пункт — с новой строки.')
    points_en = models.TextField('Задачи (EN)', blank=True)
    stack = models.CharField('Стек', max_length=300, blank=True, help_text='Например: Python · Django · React')

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Место работы'
        verbose_name_plural = 'Опыт работы'

    def __str__(self):
        return f'{self.company} — {self.title_ru}'


class ResumeProject(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField('Название', max_length=120)
    kind_ru = models.CharField('Ярлык (RU)', max_length=80, blank=True, help_text='Например: Unity 2D · WebGL')
    kind_en = models.CharField('Ярлык (EN)', max_length=80, blank=True)
    description_ru = models.TextField('Описание (RU)', blank=True)
    description_en = models.TextField('Описание (EN)', blank=True)

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name


class ResumeProjectLink(ResumeSection):
    project = models.ForeignKey(ResumeProject, on_delete=models.CASCADE, related_name='links')
    label_ru = models.CharField('Текст кнопки (RU)', max_length=60)
    label_en = models.CharField('Текст кнопки (EN)', max_length=60, blank=True)
    url = models.URLField('Ссылка', max_length=300)

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Ссылка проекта'
        verbose_name_plural = 'Ссылки проекта'

    def __str__(self):
        return f'{self.label_ru} → {self.url}'


class ResumeEducation(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    year = models.CharField('Год', max_length=20)
    place = models.CharField('Учебное заведение / курс', max_length=200)
    detail_ru = models.CharField('Описание (RU)', max_length=300, blank=True)
    detail_en = models.CharField('Описание (EN)', max_length=300, blank=True)

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'

    def __str__(self):
        return f'{self.year} — {self.place}'


class ResumeLanguage(ResumeSection):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    name_ru = models.CharField('Язык (RU)', max_length=60)
    name_en = models.CharField('Язык (EN)', max_length=60, blank=True)
    level_ru = models.CharField('Уровень (RU)', max_length=40)
    level_en = models.CharField('Уровень (EN)', max_length=40, blank=True)

    class Meta(ResumeSection.Meta):
        abstract = False
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'

    def __str__(self):
        return f'{self.name_ru} — {self.level_ru}'
