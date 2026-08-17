# Ссылки, прикрепляемые к новостям, влогам и продуктам (generic-связь).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('Backend', '0010_gameversion'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('url', models.URLField(max_length=500, verbose_name='Ссылка')),
                ('title', models.CharField(blank=True, default='', help_text='Не обязательно. Пусто — подписью станет адрес сайта.', max_length=120, verbose_name='Подпись (RU)')),
                ('title_en', models.CharField(blank=True, default='', help_text='Не обязательно. Если пусто — покажется русская подпись.', max_length=120, verbose_name='Подпись (EN)')),
                ('kind', models.CharField(choices=[('auto', 'Определить по ссылке'), ('image', 'Картинка'), ('video', 'Видеофайл'), ('embed', 'Видео с YouTube / Vimeo'), ('file', 'Файл для скачивания'), ('page', 'Обычная ссылка')], default='auto', help_text='По умолчанию тип определяется по самой ссылке: картинка — покажется картинкой, YouTube — встроенным плеером, архив — кнопкой скачивания. Меняй, только если угадало неверно.', max_length=10, verbose_name='Как показывать')),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Меньше — выше в списке.', verbose_name='Порядок')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Ссылка',
                'verbose_name_plural': 'Ссылки',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='contentlink',
            index=models.Index(fields=['content_type', 'object_id'], name='Backend_con_content_2a9c8f_idx'),
        ),
    ]
