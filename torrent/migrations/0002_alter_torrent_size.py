# Generated by Django 4.0.1 on 2022-02-01 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torrent',
            name='size',
            field=models.PositiveBigIntegerField(default=0, verbose_name='Size'),
        ),
    ]
