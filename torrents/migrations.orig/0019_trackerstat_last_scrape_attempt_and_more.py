# Generated by Django 5.1.2 on 2024-11-19 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0018_alter_tracker_is_reachable'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerstat',
            name='last_scrape_attempt',
            field=models.DateTimeField(blank=True, help_text='Last attempt to scrape this torrent on this tracker.', null=True),
        ),
        migrations.AddField(
            model_name='trackerstat',
            name='last_successful_scrape',
            field=models.DateTimeField(blank=True, help_text='The last time this torrent was successfully scraped on this tracker.', null=True),
        ),
    ]