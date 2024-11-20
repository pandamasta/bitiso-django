# Generated by Django 5.1.2 on 2024-11-16 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0015_license_website_url_en_license_website_url_fr'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='is_scrapable',
            field=models.BooleanField(default=True, help_text='Indicates whether the tracker is currently scrapable.'),
        ),
        migrations.AddField(
            model_name='tracker',
            name='last_try_date',
            field=models.DateTimeField(blank=True, help_text='Last attempt to scrape the tracker.', null=True),
        ),
    ]
