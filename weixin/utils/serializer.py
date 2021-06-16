# _*_ coding:utf-8 _*_

from rest_framework import serializers, exceptions

from account import models as Umodels
from device import models as Dmodels
from commonTool import tool


class QueryDeviceSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()

    class Meta:
        model = Dmodels.Device
        fields = ['id', 'actual_device_secret', 'module_secret', 'product_type', 'status']

    def get_status(self, row):
        return tool.data_status_transform(self.context.get('status', None))

    def get_product_type(self, row):
        return row.fk_product.product_type


class QueryPropertySerializer(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Dmodels.Device
        fields = ['id', 'product_type', 'properties']

    @staticmethod
    def get_product_type(row):
        return row.fk_product.product_key

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
