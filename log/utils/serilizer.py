# _*_ coding:utf-8 _*_

from rest_framework import serializers
from log import models
from device import models as Dmodels


class AlarmSerialiser(serializers.ModelSerializer):
    alarm_endtime = serializers.SerializerMethodField()
    alarm_starttime = serializers.SerializerMethodField()
    alarm_status = serializers.SerializerMethodField()
    from_servo = serializers.SerializerMethodField()

    class Meta:
        model = models.Alarm
        fields = '__all__'
        depth = 1

    def get_alarm_status(self, row):
        return row.get_alarm_status_display()

    def get_from_servo(self, row):
        device = Dmodels.Device.objects.filter(device_name=row.device_name).first()
        servo_num = device.from_product.product_servo_num
        if servo_num == 2:
            tmp = ['弯曲伺服', '牵引伺服']
        elif servo_num == 3:
            tmp = ['弯曲伺服', '牵引伺服', '回送伺服']
        elif servo_num == 4:
            tmp = ['左移动伺服', '左弯曲伺服', '右移动伺服', '右弯曲伺服']
        else:
            return row.from_servo

        return tmp[row.from_servo]

    def get_alarm_starttime(self, row):
        return row.alarm_starttime.strftime('%Y-%m-%d %H:%M:%S')

    def get_alarm_endtime(self, row):
        return row.alarm_endtime.strftime('%Y-%m-%d %H:%M:%S')


class RunSerialiser(serializers.ModelSerializer):
    run_starttime = serializers.SerializerMethodField()
    run_endtime = serializers.SerializerMethodField()

    class Meta:
        model = models.Run
        fields = '__all__'

    def get_run_starttime(self, row):
        return row.run_starttime.strftime('%Y-%m-%d %H:%M:%S')

    def get_run_endtime(self, row):
        if row.run_endtime is None:
            return None
        return row.run_endtime.strftime('%Y-%m-%d %H:%M:%S')
