# PendingRegistration — временный кандидат на регистрацию, живёт 24 часа,
# создаётся до подтверждения email.

from django.db import migrations, models
import Backend.models.pending_registration_model.pending_registration_model as pending


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0012_rename_backend_con_content_2a9c8f_idx_backend_con_content_a7cada_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('username', models.CharField(max_length=30)),
                ('password_hash', models.CharField(max_length=128)),
                ('token', models.CharField(db_index=True, default=pending._new_token, max_length=96, unique=True)),
                ('expires_at', models.DateTimeField(default=pending._default_expires_at)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ожидающая регистрация',
                'verbose_name_plural': 'Ожидающие регистрации',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pendingregistration',
            index=models.Index(fields=['email'], name='Backend_pen_email_a1b2c3_idx'),
        ),
    ]
