# Generated by Django 5.1.2 on 2024-11-14 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0009_torrent_status_alter_torrent_architecture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='torrent',
            name='torrent_file',
            field=models.FileField(blank=True, null=True, upload_to='torrents/', verbose_name='Torrent file'),
        ),
    ]
