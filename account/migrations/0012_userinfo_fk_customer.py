# Generated by Django 3.1.2 on 2021-05-27 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20210527_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='fk_customer',
            field=models.IntegerField(null=True),
        ),
    ]
