# Generated by Django 4.2.19 on 2025-03-27 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_credit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="credit",
            field=models.IntegerField(default=150),
        ),
    ]
