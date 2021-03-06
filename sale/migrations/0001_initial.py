# Generated by Django 3.1.2 on 2021-05-26 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SalesInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=64, unique=True, verbose_name='客户代码')),
                ('sell_time', models.DateTimeField(null=True, verbose_name='销售时间')),
                ('sell_code', models.CharField(max_length=64, null=True, verbose_name='销售订单号')),
                ('sell_site', models.CharField(max_length=128, null=True, verbose_name='销售地点')),
            ],
        ),
    ]
