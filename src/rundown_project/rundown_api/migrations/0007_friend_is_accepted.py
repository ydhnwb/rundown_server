# Generated by Django 3.0.2 on 2020-01-31 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rundown_api', '0006_auto_20200131_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
    ]