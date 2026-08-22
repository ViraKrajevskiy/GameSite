# Добавляет parent FK на всех трёх моделях комментариев (News/Vlogs/Games)
# для поддержки одноуровневых веток (реплаев). Плюс ordering по created_at.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0014_pendingpasswordreset'),
    ]

    operations = [
        migrations.AddField(
            model_name='newscomment',
            name='parent',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies', to='Backend.newscomment',
            ),
        ),
        migrations.AlterModelOptions(
            name='newscomment',
            options={'ordering': ['created_at']},
        ),
        migrations.AddField(
            model_name='vlogscomment',
            name='parent',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies', to='Backend.vlogscomment',
            ),
        ),
        migrations.AlterModelOptions(
            name='vlogscomment',
            options={'ordering': ['created_at']},
        ),
        migrations.AddField(
            model_name='gamescomment',
            name='parent',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='replies', to='Backend.gamescomment',
            ),
        ),
        migrations.AlterModelOptions(
            name='gamescomment',
            options={'ordering': ['created_at']},
        ),
    ]
