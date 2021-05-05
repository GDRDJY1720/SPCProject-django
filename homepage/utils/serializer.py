# _*_ coding:utf-8 _*_

from rest_framework import serializers

from product import models as Pmodels
from device import models as Dmodels
from log import models as Lmodels


class ProductCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Pmodels.Product
        fields = ['id', 'productname', 'count']

    def get_count(self, row):
        return Dmodels.Device.objects.filter(from_product_id=row.id).count()


class AlarmLogSerializer(serializers.ModelSerializer):
    alarmName = serializers.SerializerMethodField()
    alarmStatus = serializers.SerializerMethodField()
    servoName = serializers.SerializerMethodField()

    class Meta:
        model = Lmodels.Alarm
        fields = ['device_name', 'alarmName', 'alarmStatus', 'servoName']

    def get_alarmName(self, row):
        return row.from_alarm_info.alarm_name

    def get_alarmStatus(self, row):
        return row.get_alarm_status_display()

    def get_servoName(self, row):
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

