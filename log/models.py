from django.db import models


# Create your models here.

class Alarm(models.Model):
    alarm_status_list = [
        (0, '报警解除'),
        (1, '正在报警')
    ]
    servo_list = [
        (1, 'Error_1'),
        (2, 'Error_2'),
        (3, 'Error_3'),
        (4, 'Error_4')
    ]

    device_name = models.CharField('设备标识名称', max_length=64)
    fk_device = models.ForeignKey(to='device.Device', on_delete=models.CASCADE)
    from_servo = models.IntegerField(choices=servo_list)
    from_alarm_info = models.ForeignKey(to='AlarmInfo', on_delete=models.DO_NOTHING)
    alarm_starttime = models.DateTimeField()
    alarm_endtime = models.DateTimeField(null=True)
    alarm_status = models.IntegerField(choices=alarm_status_list)


class AlarmInfo(models.Model):
    alarm_name = models.CharField(max_length=16)
    alarm_info = models.CharField(max_length=32)


class Run(models.Model):
    device_name = models.CharField('设备标识名称', max_length=64)
    fk_device = models.ForeignKey(to='device.Device', on_delete=models.CASCADE)
    run_starttime = models.DateTimeField()
    run_endtime = models.DateTimeField(null=True)
