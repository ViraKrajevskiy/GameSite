import django.db.models.deletion
from django.db import migrations, models
import Backend.models.pending_password_reset_model.pending_password_reset_model as pwd_reset


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0013_pendingregistration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingPasswordReset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, default=pwd_reset._new_token, max_length=96, unique=True)),
                ('expires_at', models.DateTimeField(default=pwd_reset._default_expires_at)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_resets', to='Backend.user')),
            ],
            options={
                'verbose_name': 'Токен сброса пароля',
                'verbose_name_plural': 'Токены сброса пароля',
                'ordering': ['-created_at'],
            },
        ),
    ]
