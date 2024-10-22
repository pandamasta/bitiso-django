# Generated by Django 5.1.2 on 2024-10-22 16:52

import core.user_profiles.utils
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, verbose_name='Bio')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=core.user_profiles.utils.PathAndRename('profile_pics/'), validators=[core.user_profiles.utils.validate_image_type, core.user_profiles.utils.validate_file_size], verbose_name='Profile Picture')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
