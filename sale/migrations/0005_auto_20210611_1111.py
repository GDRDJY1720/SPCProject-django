# Generated by Django 3.1.2 on 2021-06-11 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0004_salesinfo_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinfo',
            name='sell_time',
            field=models.DateField(null=True, verbose_name='销售时间'),
        ),
    ]