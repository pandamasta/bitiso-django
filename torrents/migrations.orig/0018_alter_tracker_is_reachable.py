# Generated by Django 5.1.2 on 2024-11-19 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0017_tracker_failed_attempts_tracker_is_reachable_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracker',
            name='is_reachable',
            field=models.BooleanField(default=True, help_text='Indicates whether the tracker is reachable at the network level.'),
        ),
    ]
