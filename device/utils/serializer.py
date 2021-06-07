# _*_ coding:utf-8 _*_

from device import models
from product import models as Pmodels
from sale import models  as Smodels
from commonTool import tool
from rest_framework import serializers


class DeviceSerializer(serializers.ModelSerializer):
    fk_user = serializers.SerializerMethodField()  # 自定义显示
    status = serializers.SerializerMethodField()
    fk_sales = serializers.SerializerMethodField()

    class Meta:
        model = models.Device
        fields = '__all__'
        # exclude = ["fk_sales"]
        # fields = ['id', 'nick_name', 'fk_product', 'fk_user']
        # fields = ['id', 'device_name']
        depth = 1

    def get_fk_user(self, row):
        # try:
        #     ret = row.fk_user.username
        # except Exception:
        #     ret = None
        # return ret
        return None

    def get_status(self, row):
        if not self.context.get('data', None):
            return None

        for i in self.context.get('data', None):
            if row.iot_id == i.get('IotId'):
                return {
                    'status': tool.data_status_transform(i.get('Status')),
                    'last_line': i.get('LastOnlineTime', None)
                }
        return None

    def get_fk_sales(self, row):
        res = {}
        if row.fk_sales is None:
            for k in row.fk_sales.__dict__.keys():
                if k != '_state' and k != 'id':
                    res[k] = None
        else:
            for k in row.fk_sales.__dict__.keys():
                if k != '_state' and k != 'id':
                    t = getattr(row.fk_sales, k)
                    if k == 'sell_time':
                        res[k] = t.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        res[k] = t

        return res

    def get_sell_code(self, row):
        if row.fk_sales is None:
            return None

    def get_sell_site(self, row):
        if row.fk_sales is None:
            return None

    def get_sell_time(self, row):
        if row.fk_sales is None:
            return None
        return row.fk_sales.sell_time.strftime('%Y-%m-%d %H:%M:%S')


class PropertySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='fk_product.product_name')
    servo_count = serializers.SerializerMethodField()
    servo_info = serializers.SerializerMethodField()

    class Meta:
        model = models.Device
        fields = ['id', 'nick_name', 'product_name', 'servo_count', 'servo_info']

    def get_servo_count(self, row):
        if not self.context.get('servo_num', None):
            return None
        return self.context.get('servo_num', None)

    def get_servo_info(self, row):
        if not self.context.get('data', None):
            return None
        return self.context.get('data', None)


class SetPropertySerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Pmodels.Product
        fields = ['id', 'product_key', 'properties']

    def get_properties(self, row):
        tmp_dic = self.context.get('data')
        return self.format_property_data(tmp_dic)

    @staticmethod
    def format_property_data(dic):
        result = {}
        for d in dic:
            identifier_name = d.get('name').split('度')[0] + '度'
            output_data = {
                'name': d.get('name'),
                'identifier': d.get('identifier'),
                'unit': d.get('dataSpecs').get('unit'),
                'max': d.get('dataSpecs').get('max'),
                'min': d.get('dataSpecs').get('min'),
                'step': d.get('dataSpecs').get('step')
            }
            try:
                result[identifier_name].append(output_data)
            except KeyError:
                result[identifier_name] = []
                result[identifier_name].append(output_data)

        return result