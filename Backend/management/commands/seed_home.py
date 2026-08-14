r"""
Заполняет первый экран главной страницы тем, что сейчас на сайте.

Запуск (из корня проекта):
    .\.venv\Scripts\python.exe manage.py seed_home

Картинку в блок справа загрузишь сам через админку — команда её не трогает.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from Backend.models.home_model.home_model import HomeHero, HeroStat

HERO = {
    'show_badge': True,
    'badge_ru': 'Игры · приложения · код',
    'badge_en': 'Games · apps · code',

    'title_ru': 'Делаю игры',
    'title_en': 'I build games',
    'title_accent_ru': 'и приложения.',
    'title_accent_en': 'and apps.',

    'show_deck': True,
    'deck_ru': 'Портфолио разработчика: Unity-игры, веб-приложения на Python/Django и React. '
               'Здесь всё, что я собрал — с ссылками на билды, код и описанием того, как это устроено.',
    'deck_en': 'A developer portfolio: Unity games and web apps built with Python/Django and React. '
               'Everything I have shipped, with links to builds, source code and notes on how it works.',

    'show_btn1': True,
    'btn1_text_ru': 'Смотреть работы →',
    'btn1_text_en': 'See the work →',
    'btn1_url': '/games',

    'show_btn2': True,
    'btn2_text_ru': 'Моё резюме',
    'btn2_text_en': 'My résumé',
    'btn2_url': '/about',

    'show_stats': True,

    'show_art': True,
    'art_title_ru': 'PIZZA',
    'art_title_en': 'PIZZA',
    'art_url': 'https://virakrajevskiy.itch.io/pizza',

    'show_score': False,
    'score': '',
    'score_label_ru': 'из 10',
    'score_label_en': 'out of 10',
}

STATS = [
    ('1.5', 'года в разработке', 'years building'),
    ('5+', 'проектов', 'projects shipped'),
    ('2', 'стека: backend и gamedev', 'stacks: backend and gamedev'),
]


class Command(BaseCommand):
    help = 'Заполняет первый экран главной страницы данными по умолчанию.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Перезаписать первый экран, даже если он уже есть в базе.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        existing = HomeHero.objects.first()

        if existing and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'Первый экран уже есть в базе (id={existing.pk}). '
                f'Запусти с --force, чтобы перезаписать его.'
            ))
            return

        if existing:
            HomeHero.objects.all().delete()
            self.stdout.write('Старый первый экран удалён.')

        hero = HomeHero.objects.create(is_active=True, **HERO)

        for order, (num, label_ru, label_en) in enumerate(STATS):
            HeroStat.objects.create(
                hero=hero, order=order, num=num, label_ru=label_ru, label_en=label_en,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Первый экран создан (id={hero.pk}). '
            f'Правь его в админке: /admin/Backend/homehero/{hero.pk}/change/'
        ))
