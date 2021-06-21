# Generated by Django 3.1.2 on 2021-06-21 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_loginlog'),
        ('device', '0034_device_device_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='LockLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operate', models.CharField(max_length=16)),
                ('start_time', models.DateTimeField()),
                ('fk_device', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='device.device')),
                ('fk_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='account.userinfo')),
            ],
        ),
    ]
