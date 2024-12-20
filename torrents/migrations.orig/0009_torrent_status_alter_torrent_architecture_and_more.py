# Generated by Django 5.1.2 on 2024-11-11 21:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0008_remove_torrent_original_file_path_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='torrent',
            name='status',
            field=models.CharField(choices=[('active', 'Active - visible to all'), ('pending', 'Pending validation'), ('blocked', 'Blocked'), ('deleted', 'Deleted')], default='pending', max_length=10, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='torrent',
            name='architecture',
            field=models.CharField(blank=True, choices=[('i386', 'i386'), ('amd64', 'amd64'), ('arm64', 'ARM64'), ('arm', 'ARM'), ('other', 'Other')], max_length=10, null=True, verbose_name='Architecture'),
        ),
        migrations.AlterField(
            model_name='torrent',
            name='os',
            field=models.CharField(blank=True, choices=[('linux', 'Linux'), ('windows', 'Windows'), ('macos', 'MacOS'), ('android', 'Android'), ('bsd', 'BSD')], max_length=10, null=True, verbose_name='Operating System'),
        ),
        migrations.AddIndex(
            model_name='torrent',
            index=models.Index(fields=['status'], name='torrents_to_status_4e05b4_idx'),
        ),
    ]
