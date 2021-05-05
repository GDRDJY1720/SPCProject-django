# _*_ coding:utf-8 _*_

from product import models
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = '__all__'
        # depth = 1

    def get_data(self, row):
        data = self.context.get('data', None)
        if not data:
            return None

        return {'Description': data.get('Description'), 'DeviceCount': data.get('DeviceCount')}

