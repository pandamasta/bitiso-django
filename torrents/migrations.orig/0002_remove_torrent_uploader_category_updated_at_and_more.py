# Generated by Django 5.1.2 on 2024-10-23 20:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='torrent',
            name='uploader',
        ),
        migrations.AddField(
            model_name='category',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='category',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='torrent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='torrent',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='torrents', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='torrent',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
    ]
