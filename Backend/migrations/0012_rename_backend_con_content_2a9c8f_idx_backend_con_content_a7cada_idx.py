from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0011_contentlink'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='contentlink',
            new_name='Backend_con_content_a7cada_idx',
            old_name='Backend_con_content_2a9c8f_idx',
        ),
    ]
