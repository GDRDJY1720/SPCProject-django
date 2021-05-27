from django.db import models


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=32)
    product_key = models.CharField(max_length=64)
    product_servo_num = models.IntegerField(null=True)
    product_type = models.CharField(max_length=18, default='test')
    product_identifier = models.CharField(max_length=10, null=True)
