# Generated by Django 3.1.2 on 2021-05-26 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0024_remove_device_fk_sales'),
        ('sale', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesinfo',
            name='fk_devices',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='device.device'),
        ),
    ]