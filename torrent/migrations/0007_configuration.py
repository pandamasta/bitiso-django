# Generated by Django 4.2.3 on 2023-08-06 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torrent', '0006_rename_donnees_listeintermediaire_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
