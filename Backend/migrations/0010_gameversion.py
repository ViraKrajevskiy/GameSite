# Версии продукта: номер, дата, что нового, ссылка на скачивание.

import django.db.models.deletion
import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0009_news_kind_vlogs_kind'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number', models.CharField(help_text='Как пишешь сам: 1.0, 1.2.3, v2 beta — что угодно.', max_length=30, verbose_name='Версия')),
                ('released_at', models.DateField(blank=True, help_text='Не обязательно. Без даты версия встанет в конец списка.', null=True, verbose_name='Дата выхода')),
                ('changelog', models.TextField(blank=True, default='', help_text='Не обязательно. Каждый пункт с новой строки.', verbose_name='Что нового (RU)')),
                ('changelog_en', models.TextField(blank=True, default='', help_text='Не обязательно. Если пусто — на английской версии покажется русский текст.', verbose_name='Что нового (EN)')),
                ('url', models.URLField(blank=True, default='', help_text='Не обязательно. Ссылка именно на эту версию, если она своя.', verbose_name='Ссылка на скачивание')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='Backend.games')),
            ],
            options={
                'verbose_name': 'Версия продукта',
                'verbose_name_plural': 'Версии продукта',
                'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('released_at'), descending=True, nulls_last=True), '-id'],
                'unique_together': {('game', 'number')},
            },
        ),
    ]
