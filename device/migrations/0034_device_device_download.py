# Generated by Django 3.1.2 on 2021-06-19 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0033_auto_20210618_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='device_download',
            field=models.BooleanField(default=False, verbose_name='信息下载标志'),
        ),
    ]
