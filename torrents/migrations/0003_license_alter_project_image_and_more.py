# Generated by Django 5.1.2 on 2024-11-04 22:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0002_remove_torrent_uploader_category_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='License name')),
                ('description', models.TextField(blank=True, default='', verbose_name='License description')),
            ],
            options={
                'verbose_name': 'License',
                'verbose_name_plural': 'Licenses',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='project',
            name='image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='img/project/original/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='large_image',
            field=models.ImageField(blank=True, default='', upload_to='img/project/large/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='medium_image',
            field=models.ImageField(blank=True, default='', upload_to='img/project/medium/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='mini_image',
            field=models.ImageField(blank=True, default='', upload_to='img/project/mini/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='small_image',
            field=models.ImageField(blank=True, default='', upload_to='img/project/small/'),
        ),
        migrations.AlterField(
            model_name='torrent',
            name='is_bitiso',
            field=models.BooleanField(default=True, verbose_name='Created by Bitiso?'),
        ),
        migrations.AddField(
            model_name='project',
            name='license',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='torrents.license', verbose_name='Default license'),
        ),
        migrations.AddField(
            model_name='torrent',
            name='license',
            field=models.ForeignKey(blank=True, help_text='Overrides project license if specified', null=True, on_delete=django.db.models.deletion.SET_NULL, to='torrents.license', verbose_name='License'),
        ),
    ]