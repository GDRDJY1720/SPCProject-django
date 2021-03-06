# Generated by Django 3.1.2 on 2021-04-06 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0011_auto_20210325_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_name',
            field=models.CharField(max_length=64, unique=True, verbose_name='设备标识名称'),
        ),
        migrations.AlterField(
            model_name='device',
            name='device_secret',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='iot_id',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
