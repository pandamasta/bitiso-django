# Generated by Django 4.0.1 on 2022-01-27 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrent', '0006_tracker_torrent_comment_torrent_trackers'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='name',
            field=models.CharField(default='NONAME', max_length=32),
        ),
    ]
