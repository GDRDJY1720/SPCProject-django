# Generated by Django 3.1.2 on 2021-05-27 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0025_device_fk_sales'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='from_product',
            new_name='fk_product',
        ),
    ]
