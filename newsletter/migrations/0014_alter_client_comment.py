# Generated by Django 5.1.3 on 2024-11-21 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0013_alter_mailing_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="comment",
            field=models.TextField(blank=True, null=True, verbose_name="Комментарий"),
        ),
    ]
