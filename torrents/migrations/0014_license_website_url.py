# Generated by Django 5.1.2 on 2024-11-15 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrents', '0013_category_description_en_category_description_fr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='website_url',
            field=models.URLField(blank=True, max_length=2000, null=True, verbose_name='Official website URL'),
        ),
    ]