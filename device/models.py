from django.db import models


# Create your models here.

class Device(models.Model):
    nick_name = models.CharField('设备备注名称', max_length=32, null=True)
    device_name = models.CharField('设备标识名称', max_length=64, unique=True)
    device_secret = models.CharField(max_length=64, unique=True)
    iot_id = models.CharField(max_length=64, unique=True)
    device_product_name = models.CharField(max_length=32, null=True)
    fk_product = models.ForeignKey(to='product.Product', on_delete=models.CASCADE)
    fk_user = models.ForeignKey(to='account.UserInfo', on_delete=models.DO_NOTHING, default=1, null=True)
    fk_sales = models.ForeignKey(to='sale.SalesInfo', on_delete=models.SET_NULL, null=True)
    actual_device_secret = models.CharField('设备序列号', max_length=32, null=True, unique=True)
    module_secret = models.CharField(max_length=32, null=True, unique=True)
    module_secret_two = models.CharField(max_length=32, null=True, unique=True)
    hmi_secret = models.CharField(max_length=32, null=True, unique=True)
    device_lock = models.BooleanField(default=False)
    device_type = models.IntegerField(default=2)
    device_longitude = models.FloatField(default=103.984727)
    device_latitude = models.FloatField(default=30.969819)
    device_province = models.CharField(max_length=6, default='四川')
    device_TotalRunTime = models.IntegerField(default=0)
    device_TotalOutput = models.IntegerField(default=0)

    device_DelayLock = models.BooleanField('延迟锁定标志', default=False)
    device_lock_status = models.BooleanField('设备锁定状态', default=False)
    device_date = models.DateField('延迟日期', null=True)
    device_download = models.BooleanField('信息下载标志', default=False)


class LockLog(models.Model):
    fk_user = models.ForeignKey(to='account.UserInfo', on_delete=models.DO_NOTHING)
    fk_device = models.ForeignKey(to='Device', on_delete=models.DO_NOTHING)
    operate = models.CharField(max_length=16)
    start_time = models.DateTimeField()
