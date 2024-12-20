# Generated by Django 5.1.2 on 2024-10-22 22:01

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
            name='Tracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=1000, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Tracker',
                'verbose_name_plural': 'Trackers',
                'ordering': ['url'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='torrents.category', verbose_name='Parent category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Project name')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='Show in the front end')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description of project')),
                ('website_url', models.URLField(blank=True, max_length=2000, null=True, verbose_name='Official website URL')),
                ('website_url_download', models.URLField(blank=True, max_length=2000, verbose_name='Download page URL')),
                ('website_url_repo', models.URLField(blank=True, max_length=2000, verbose_name='Repository URL')),
                ('image', models.ImageField(blank=True, null=True, upload_to='img/project/original/')),
                ('mini_image', models.ImageField(blank=True, upload_to='img/project/mini/')),
                ('small_image', models.ImageField(blank=True, upload_to='img/project/small/')),
                ('medium_image', models.ImageField(blank=True, upload_to='img/project/medium/')),
                ('large_image', models.ImageField(blank=True, upload_to='img/project/large/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deleted at')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Torrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_hash', models.CharField(max_length=40, unique=True, verbose_name='SHA1 of torrent')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('size', models.PositiveBigIntegerField(default=0, verbose_name='Size in bytes')),
                ('pieces', models.PositiveIntegerField(default=1, verbose_name='Number of pieces')),
                ('piece_size', models.PositiveIntegerField(default=0, verbose_name='Piece size in bytes')),
                ('magnet', models.TextField(default='N/A', verbose_name='Magnet URI')),
                ('torrent_filename', models.CharField(default='N/A', max_length=128, verbose_name='Torrent file name')),
                ('comment', models.CharField(default='N/A', max_length=256, verbose_name='Comment')),
                ('file_list', models.TextField(default='N/A', verbose_name='List of files')),
                ('file_count', models.PositiveIntegerField(default=1, verbose_name='Number of files')),
                ('is_active', models.BooleanField(default=False, verbose_name='Show in the front end')),
                ('is_bitiso', models.BooleanField(default=True, verbose_name='Created by bitiso?')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('website_url', models.URLField(blank=True, max_length=2000, null=True, verbose_name='Official website URL')),
                ('website_url_download', models.URLField(blank=True, max_length=2000, verbose_name='Download page URL')),
                ('website_url_repo', models.URLField(blank=True, max_length=2000, verbose_name='Repository URL')),
                ('version', models.CharField(blank=True, max_length=16, verbose_name='Version of the software')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Deletion timestamp')),
                ('seed_count', models.PositiveIntegerField(default=0, verbose_name='Number of seeds')),
                ('leech_count', models.PositiveIntegerField(default=0, verbose_name='Number of leeches')),
                ('download_count', models.PositiveIntegerField(default=0, verbose_name='Number of downloads')),
                ('completion_count', models.PositiveIntegerField(default=0, verbose_name='Number of completions')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='torrents.category', verbose_name='Category')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='torrents', to='torrents.project', verbose_name='Project')),
                ('uploader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Uploader')),
            ],
            options={
                'verbose_name': 'Torrent',
                'verbose_name_plural': 'Torrents',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TrackerStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('announce_priority', models.IntegerField(default=0, verbose_name='Announce priority')),
                ('seed', models.PositiveIntegerField(default=0, verbose_name='Number of seeds')),
                ('leech', models.PositiveIntegerField(default=0, verbose_name='Number of leeches')),
                ('complete', models.PositiveIntegerField(default=0, verbose_name='Complete')),
                ('torrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torrents.torrent')),
                ('tracker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='torrents.tracker')),
            ],
            options={
                'verbose_name': 'Tracker Stat',
                'verbose_name_plural': 'Tracker Stats',
                'ordering': ['torrent', 'tracker'],
            },
        ),
        migrations.AddField(
            model_name='torrent',
            name='trackers',
            field=models.ManyToManyField(through='torrents.TrackerStat', to='torrents.tracker'),
        ),
        migrations.AddConstraint(
            model_name='trackerstat',
            constraint=models.UniqueConstraint(fields=('torrent', 'tracker'), name='unique_torrent_tracker'),
        ),
    ]
