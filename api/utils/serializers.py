# _*_ coding:utf-8 _*_

from rest_framework import serializers, exceptions

from account import models as Umodels
from product import models as Pmodels
from device import models as Dmodels
from commonTool import tool


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(error_messages={'required': '不能为空'})
    user_secret = serializers.CharField(error_messages={'required': '不能为空'})

    def validate(self, data):
        user = Umodels.UserInfo.objects.filter(user_id=data.get('user_id'), user_secret=data.get('user_secret')).first()
        if not user:
            raise serializers.ValidationError(detail='用户不存在', code=1001)

        self.context['user'] = user
        return data


class QueryDeviceListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()  # 自定义显示
    product_key = serializers.SerializerMethodField()

    class Meta:
        model = Dmodels.Device
        fields = ['actual_device_secret', 'product_name', 'product_key', 'status']

    def get_product_name(self, row):
        return row.from_product.productname

    def get_product_key(self, row):
        return row.from_product.productkey

    def get_status(self, row):
        for s in self.context.get('status'):
            if s.get('IotId') == row.iot_id:
                return tool.data_status_transform(s.get('Status'))


class SetPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dmodels.Device
        fields = '__all__'


class QueryProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pmodels.Product
        fields = ['productname', 'productkey']
