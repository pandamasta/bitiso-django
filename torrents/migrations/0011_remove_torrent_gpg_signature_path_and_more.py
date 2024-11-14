# Generated by Django 5.1.2 on 2024-11-14 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0010_torrent_torrent_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='torrent',
            name='gpg_signature_path',
        ),
        migrations.AddField(
            model_name='torrent',
            name='gpg_signature',
            field=models.FileField(blank=True, null=True, upload_to='torrents/', verbose_name='GPG signature file'),
        ),
    ]
