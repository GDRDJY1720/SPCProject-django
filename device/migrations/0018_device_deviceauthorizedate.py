# Generated by Django 3.1.2 on 2021-05-18 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0017_device_deviceonlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='deviceAuthorizeDate',
            field=models.DateTimeField(null=True),
        ),
    ]
