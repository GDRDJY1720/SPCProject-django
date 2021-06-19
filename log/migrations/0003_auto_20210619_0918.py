# Generated by Django 3.1.2 on 2021-06-19 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0033_auto_20210618_1751'),
        ('log', '0002_auto_20210322_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='fk_device',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='device.device'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='run',
            name='fk_device',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='device.device'),
            preserve_default=False,
        ),
    ]
