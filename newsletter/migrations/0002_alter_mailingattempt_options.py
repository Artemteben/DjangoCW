# Generated by Django 5.1.3 on 2024-11-13 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mailingattempt",
            options={
                "verbose_name": "Попытка рассылки",
                "verbose_name_plural": "Попытки рассылки",
            },
        ),
    ]
