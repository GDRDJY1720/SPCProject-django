# Generated by Django 3.1.2 on 2021-06-07 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0003_remove_salesinfo_fk_devices'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesinfo',
            name='company_name',
            field=models.CharField(max_length=64, null=True, verbose_name='公司名称'),
        ),
    ]
