# Generated by Django 3.1.2 on 2021-05-18 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0016_auto_20210429_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='deviceOnLock',
            field=models.BooleanField(default=False),
        ),
    ]
