# Generated by Django 5.1.2 on 2024-11-20 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0023_tracker_is_reachable_mode_tracker_is_scrapable_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='torrent_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of Torrents'),
        ),
    ]
