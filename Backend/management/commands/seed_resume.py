r"""
Заполняет базу резюме теми данными, что сейчас лежат на странице «О нас».

Запуск (из корня проекта):
    .\.venv\Scripts\python.exe manage.py seed_resume

Повторный запуск ничего не ломает: старое резюме с тем же именем очищается
и заполняется заново. Если хочешь перезаписать вручную отредактированные
данные — добавь --force.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from Backend.models.resume_model.resume_model import (
    Resume, ResumeContact, ResumeFact, ResumeSkillGroup, ResumeExperience,
    ResumeProject, ResumeProjectLink, ResumeEducation, ResumeLanguage,
)

RESUME = {
    'name_ru': 'Кабулов Камолиддин',
    'name_en': 'Kamoliddin Kabulov',
    'role_ru': 'Fullstack-разработчик · Python / Django · Unity',
    'role_en': 'Fullstack Developer · Python / Django · Unity',
    'tagline_ru': 'Делаю бэкенды на Python/Django и игры на Unity. Этот сайт — мой каталог игр и портфолио одновременно.',
    'tagline_en': 'I build backends with Python/Django and games with Unity. This site is my game catalog and portfolio in one.',
    'about_ru': (
        'Уверенный Python/Django backend-разработчик. Есть опыт коммерческой разработки '
        '(сайт художника, LMS/CRM-система, B2B-платформы) и опыт полного цикла: проектирование '
        'моделей данных, REST API, документация в Swagger, деплой на Nginx + Gunicorn.\n'
        'Параллельно занимаюсь геймдевом на Unity: понимаю игровую логику, 2D-физику и компонентную '
        'архитектуру, довожу игру до играбельного состояния и публикую билды. Быстро обучаюсь, '
        'могу вести проект с нуля.'
    ),
    'about_en': (
        'Confident Python/Django backend developer with commercial experience (artist portfolio site, '
        'an LMS/CRM system, B2B platforms) and full-cycle skills: data modeling, REST API design, '
        'Swagger documentation and deployment on Nginx + Gunicorn.\n'
        'In parallel I work on Unity game development: I understand gameplay logic, 2D physics and '
        'component-based architecture, and I take a game to a playable state and publish builds. '
        'I learn fast and can drive a project from scratch.'
    ),
    'cta_title_ru': 'Открыт к работе',
    'cta_title_en': 'Open to work',
    'cta_text_ru': 'Backend, fullstack или Unity — пишите в Telegram или на почту.',
    'cta_text_en': 'Backend, fullstack or Unity — reach me on Telegram or by email.',
    'cta_btn1_text_ru': 'Написать в Telegram',
    'cta_btn1_text_en': 'Message on Telegram',
    'cta_btn1_url': 'https://t.me/Vira_Krajevskiy',
    'cta_btn2_text_ru': 'Смотреть GitHub',
    'cta_btn2_text_en': 'Browse GitHub',
    'cta_btn2_url': 'https://github.com/ViraKrajevskiy',
}

CONTACTS = [
    ('Telegram', 'Telegram', '@Vira_Krajevskiy', 'https://t.me/Vira_Krajevskiy'),
    ('Телефон', 'Phone', '+998 (90) 036-80-52', 'tel:+998900368052'),
    ('Email', 'Email', 'guidevirgate@gmail.com', 'mailto:guidevirgate@gmail.com'),
    ('GitHub', 'GitHub', 'ViraKrajevskiy', 'https://github.com/ViraKrajevskiy'),
    ('itch.io', 'itch.io', 'virakrajevskiy.itch.io', 'https://virakrajevskiy.itch.io'),
    ('LinkedIn', 'LinkedIn', 'vira-krajevskiy', 'https://www.linkedin.com/in/vira-krajevskiy-9502662a6'),
]

FACTS = [
    ('1.5', 'года опыта', 'years of experience'),
    ('5+', 'проектов', 'projects shipped'),
    ('3', 'языка (C2)', 'languages (C2)'),
]

SKILL_GROUPS = [
    ('Backend', 'Backend',
     'Python, Django, Django REST Framework, REST API, ORM, JWT / Token Auth, OOP, MVT'),
    ('Базы данных', 'Databases',
     'PostgreSQL, pgAdmin, MySQL, SQLite, Оптимизация запросов'),
    ('Frontend', 'Frontend',
     'React, JavaScript (ES6+), HTML5, CSS3, Bootstrap, Figma'),
    ('GameDev', 'GameDev',
     'Unity 2D, C#, Gameplay-программирование, 2D Physics, UGUI, Particle System, Level Design, Blender (база)'),
    ('DevOps', 'DevOps',
     'Nginx, Gunicorn, Docker, docker-compose, Linux, DigitalOcean, Deploy'),
    ('Инструменты', 'Tools',
     'Git, GitHub, Swagger UI, Postman, JetBrains, VS Code, itch.io'),
]

EXPERIENCE = [
    {
        'period_ru': 'Июнь 2026 — Август 2026',
        'period_en': 'June 2026 — August 2026',
        'company': 'ONESEC',
        'place_ru': 'Ташкент',
        'place_en': 'Tashkent',
        'title_ru': 'Junior системный аналитик (Tech / QA / Analytics)',
        'title_en': 'Junior Systems Analyst (Tech / QA / Analytics)',
        'points_ru': (
            'Ручное тестирование лендинга: баги, UX-проблемы, структурированный баг-репорт с рекомендациями для руководства.\n'
            'SEO-аудит и оптимизация сайта: анализ, внедрение правок, контроль результата.\n'
            'Продуктовая аналитика: сравнение конкурентов, актуализация и переработка User Stories.\n'
            'Сопровождение цикла доработки лендинга от анализа до релиза.'
        ),
        'points_en': (
            'Manual testing of the landing page: found bugs and UX issues, wrote a structured bug report with recommendations for management.\n'
            'SEO audit and optimization: analysis, implementation of fixes, result tracking.\n'
            'Product analytics: competitor comparison, refreshing and reworking User Stories.\n'
            'Owned the landing page improvement cycle from analysis to release.'
        ),
        'stack': '',
    },
    {
        'period_ru': 'Февраль 2026 — Июнь 2026',
        'period_en': 'February 2026 — June 2026',
        'company': 'Swift Intel',
        'place_ru': 'Ташкент',
        'place_en': 'Tashkent',
        'title_ru': 'Fullstack-разработчик (Python / Django / React)',
        'title_en': 'Fullstack Developer (Python / Django / React)',
        'points_ru': (
            'Спроектировал и реализовал с нуля архитектуру LMS-системы для учебного центра: ролевая модель '
            '(Студент / Преподаватель / Администратор), модули успеваемости, автоматизированный учёт оплат.\n'
            'Покрыл бэкенд автодокументацией Swagger UI для прозрачной интеграции с фронтендом.\n'
            'Проектировал архитектуру и бизнес-логику B2B-платформ; делал UI/UX-макеты и прототипы в Figma '
            'и переносил их в адаптивную вёрстку с React-компонентами.\n'
            'Развивал корпоративный таск-трекер (аналог Trello): оптимизация SQL-запросов, конфигурация серверного '
            'окружения, архитектура мультиязычности и полная локализация интерфейса на китайский.'
        ),
        'points_en': (
            'Designed and built an LMS architecture from scratch for a training center: role model '
            '(Student / Teacher / Admin), performance modules, automated payment tracking.\n'
            'Covered the backend with Swagger UI auto-documentation for transparent frontend integration.\n'
            'Designed architecture and business logic for B2B products; produced UI/UX mockups and prototypes '
            'in Figma and turned them into responsive markup with React components.\n'
            'Maintained a corporate task tracker (Trello-like): SQL query optimization, server environment '
            'configuration, multilingual architecture and full UI localization into Chinese.'
        ),
        'stack': 'Python · Django · DRF · React · Swagger UI · SQL · Bootstrap',
    },
    {
        'period_ru': 'Декабрь 2025 — Январь 2026',
        'period_en': 'December 2025 — January 2026',
        'company': '8Bit Games',
        'place_ru': 'Удалённо',
        'place_en': 'Remote',
        'title_ru': 'Unity Developer (Intern)',
        'title_en': 'Unity Developer (Intern)',
        'points_ru': (
            'Проект «PIZZA» — 2D физическая игра-головоломка в жанре Merge Puzzle (аналог Suika Game).\n'
            'Реализовал игровую логику на C#: спавн, падение, столкновения и объединение (merge) объектов.\n'
            'Настроил физику через Rigidbody2D и Physics Material 2D для предсказуемого и «сочного» геймплея.\n'
            'Разработал систему прогрессии и подсчёта очков, спроектировал уровень и баланс спавна.\n'
            'Интегрировал UI (меню, экран счёта) и визуальные эффекты слияния через Particle System.'
        ),
        'points_en': (
            'Project "PIZZA" — a 2D physics merge-puzzle game (Suika Game style).\n'
            'Implemented core gameplay in C#: spawning, dropping, collisions and object merging.\n'
            'Tuned physics via Rigidbody2D and Physics Material 2D for predictable, juicy gameplay.\n'
            'Built the progression and scoring system, designed the play space and spawn balance.\n'
            'Integrated UI (menu, score screen) and merge VFX with the Particle System.'
        ),
        'stack': 'Unity · C# · 2D Physics · UGUI · Particle System',
    },
    {
        'period_ru': 'Май 2025 — Сентябрь 2025',
        'period_en': 'May 2025 — September 2025',
        'company': 'Freelance / Upwork',
        'place_ru': 'Ташкент',
        'place_en': 'Tashkent',
        'title_ru': 'Fullstack-разработчик — сайт-портфолио художника Алишера Мирзо',
        'title_en': 'Fullstack Developer — portfolio site for artist Alisher Mirzo',
        'points_ru': (
            'Спроектировал структуру БД в PostgreSQL и оптимизировал работу с ней через Psycopg2.\n'
            'Реализовал регистрацию и роли пользователей, ленту новостей, лайки и комментарии (CRUD).\n'
            'Разработал REST API для разделения бэкенда и фронтенда.\n'
            'Настроил боевое окружение на DigitalOcean: Nginx как reverse-proxy, Gunicorn как WSGI-сервер, '
            'безопасность, статика и медиа.\n'
            'Поддерживал проект после релиза.'
        ),
        'points_en': (
            'Designed the PostgreSQL schema and optimized access through Psycopg2.\n'
            'Built registration and user roles, a news feed, likes and comments (CRUD).\n'
            'Developed a REST API to separate backend and frontend logic.\n'
            'Set up production on DigitalOcean: Nginx as reverse proxy, Gunicorn as WSGI server, security, '
            'static and media handling.\n'
            'Supported the project after release.'
        ),
        'stack': 'Python · Django · DRF · PostgreSQL · Nginx · Gunicorn · DigitalOcean',
    },
    {
        'period_ru': 'Февраль 2025 — Май 2025',
        'period_en': 'February 2025 — May 2025',
        'company': 'Личный проект',
        'place_ru': '',
        'place_en': '',
        'title_ru': 'Backend-разработчик — LMS & CRM System (API-only)',
        'title_en': 'Backend Developer — LMS & CRM System (API-only)',
        'points_ru': (
            'Серверная часть LMS/CRM с фокусом на автоматизацию процессов и безопасность данных.\n'
            'Реализовал защищённый вход через OTP (одноразовый пароль).\n'
            'Спроектировал и задокументировал эндпоинты в Swagger UI — тестирование запросов без фронтенда.\n'
            'Регулярное тестирование серверной логики и целостности БД, самостоятельный деплой.'
        ),
        'points_en': (
            'Server side of an LMS/CRM focused on process automation and data security.\n'
            'Implemented secure login via OTP (one-time password).\n'
            'Designed and documented endpoints in Swagger UI — request testing without a frontend.\n'
            'Regular testing of server logic and database integrity, deployed the app myself.'
        ),
        'stack': 'Python · Django · DRF · Swagger / ReDoc · OTP Auth · Postman',
    },
]

PROJECTS = [
    {
        'name': 'PIZZA — Merge Puzzle',
        'kind_ru': 'Unity 2D · WebGL',
        'kind_en': 'Unity 2D · WebGL',
        'description_ru': 'Физическая головоломка: merge-механика объектов, физика столкновений, система очков, '
                          'UI и эффекты, настройка баланса и сложности.',
        'description_en': 'Physics puzzle game: object merge mechanics, collision physics, scoring system, '
                          'UI and effects, difficulty balancing.',
        'links': [
            ('Играть на itch.io', 'Play on itch.io', 'https://virakrajevskiy.itch.io/pizza'),
            ('GitHub', 'GitHub', 'https://github.com/ViraKrajevskiy/PizzaGameWEbGL'),
        ],
    },
    {
        'name': 'LMS / CRM System',
        'kind_ru': 'Django REST · Backend',
        'kind_en': 'Django REST · Backend',
        'description_ru': 'Система с ролями (Студент, Преподаватель, Админ), уроками, группами и домашними заданиями: '
                          'полный CRUD на DRF ViewSets, DRF Permissions, проверка дедлайнов с автоблокировкой сдачи, '
                          'загрузка файлов, оценки, документация Swagger UI, оптимизация ORM '
                          '(select_related / prefetch_related).',
        'description_en': 'Role-based system (Student, Teacher, Admin) with lessons, groups and homework: full CRUD on '
                          'DRF ViewSets, DRF Permissions, deadline checks with automatic submission lock, file uploads, '
                          'grading, Swagger UI docs, ORM optimization (select_related / prefetch_related).',
        'links': [
            ('GitHub', 'GitHub', 'https://github.com/ViraKrajevskiy/LMS-CRM-BACKEND-AND-Swagger-ui'),
        ],
    },
    {
        'name': 'Сайт художника Алишера Мирзо',
        'kind_ru': 'Fullstack · Коммерческий',
        'kind_en': 'Fullstack · Commercial',
        'description_ru': 'Сайт с личным кабинетом, лентой, лайками и комментариями. Полный цикл: бэкенд, вёрстка, '
                          'деплой на Nginx + Gunicorn, поддержка после релиза.',
        'description_en': 'Site with a user account area, feed, likes and comments. Full cycle: backend, markup, '
                          'deployment on Nginx + Gunicorn, post-release support.',
        'links': [
            ('GitHub', 'GitHub', 'https://github.com/ViraKrajevskiy/Alisher-MirzoWebsite'),
        ],
    },
    {
        'name': 'MessengerShop',
        'kind_ru': 'Django · B2B',
        'kind_en': 'Django · B2B',
        'description_ru': 'Коммерческий проект периода Swift Intel: бизнес-логика, работа с SQL и серверным окружением.',
        'description_en': 'Commercial project from the Swift Intel period: business logic, SQL work and server '
                          'environment setup.',
        'links': [
            ('GitHub', 'GitHub', 'https://github.com/ViraKrajevskiy/MessengerShop'),
        ],
    },
    {
        'name': 'GAMESITE',
        'kind_ru': 'React + Django REST',
        'kind_en': 'React + Django REST',
        'description_ru': 'Сайт, который вы сейчас читаете: каталог игр, новости, влоги, комментарии и оценки. '
                          'Фронтенд на React (Vite, роутинг, темы, i18n), бэкенд на Django REST Framework.',
        'description_en': 'The site you are reading: game catalog, news, vlogs, comments and ratings. React frontend '
                          '(Vite, routing, themes, i18n) with a Django REST Framework backend.',
        'links': [],
    },
]

EDUCATION = [
    ('2027', 'Kimyo International University in Tashkent',
     'Бакалавр · School of Engineering, Information System Engineering',
     'Bachelor · School of Engineering, Information System Engineering'),
    ('2025', 'Najot Ta’lim',
     'Python Backend Developer (Django + DRF, Swagger)',
     'Python Backend Developer (Django + DRF, Swagger)'),
    ('2025', 'Rustam IELTS',
     'Английский язык, подготовка к IELTS',
     'English language, IELTS preparation'),
    ('2026', 'Postman',
     'Сертификат: Postman Testing',
     'Certificate: Postman Testing'),
]

LANGUAGES = [
    ('Узбекский', 'Uzbek', 'Родной', 'Native'),
    ('Русский', 'Russian', 'C2', 'C2'),
    ('Английский', 'English', 'C2', 'C2'),
]


class Command(BaseCommand):
    help = 'Заполняет резюме на странице «О нас» данными по умолчанию.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Перезаписать резюме, даже если оно уже есть в базе.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        existing = Resume.objects.filter(name_ru=RESUME['name_ru']).first()

        if existing and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'Резюме «{existing}» уже есть в базе (id={existing.pk}). '
                f'Запусти с --force, чтобы перезаписать его.'
            ))
            return

        if existing:
            existing.delete()
            self.stdout.write('Старое резюме удалено.')

        resume = Resume.objects.create(is_active=True, **RESUME)

        for order, (label_ru, label_en, value, url) in enumerate(CONTACTS):
            ResumeContact.objects.create(
                resume=resume, order=order, label_ru=label_ru, label_en=label_en, value=value, url=url,
            )

        for order, (num, label_ru, label_en) in enumerate(FACTS):
            ResumeFact.objects.create(
                resume=resume, order=order, num=num, label_ru=label_ru, label_en=label_en,
            )

        for order, (title_ru, title_en, items) in enumerate(SKILL_GROUPS):
            ResumeSkillGroup.objects.create(
                resume=resume, order=order, title_ru=title_ru, title_en=title_en, items=items,
            )

        for order, job in enumerate(EXPERIENCE):
            ResumeExperience.objects.create(resume=resume, order=order, **job)

        for order, project in enumerate(PROJECTS):
            links = project.pop('links')
            obj = ResumeProject.objects.create(resume=resume, order=order, **project)
            for link_order, (label_ru, label_en, url) in enumerate(links):
                ResumeProjectLink.objects.create(
                    project=obj, order=link_order, label_ru=label_ru, label_en=label_en, url=url,
                )

        for order, (year, place, detail_ru, detail_en) in enumerate(EDUCATION):
            ResumeEducation.objects.create(
                resume=resume, order=order, year=year, place=place,
                detail_ru=detail_ru, detail_en=detail_en,
            )

        for order, (name_ru, name_en, level_ru, level_en) in enumerate(LANGUAGES):
            ResumeLanguage.objects.create(
                resume=resume, order=order, name_ru=name_ru, name_en=name_en,
                level_ru=level_ru, level_en=level_en,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Резюме «{resume}» создано (id={resume.pk}). '
            f'Правь его в админке: /admin/Backend/resume/{resume.pk}/change/'
        ))
