# Generated by Django 3.1.2 on 2021-01-29 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_userinfo_from_product'),
        ('device', '0002_device_iot_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='from_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='account.userinfo'),
        ),
    ]
