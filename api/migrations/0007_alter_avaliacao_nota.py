# Generated by Django 4.2.20 on 2025-05-06 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_delete_progresso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avaliacao',
            name='nota',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
