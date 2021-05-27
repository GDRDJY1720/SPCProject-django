# _*_ coding:utf-8 _*_

from sale import models

from rest_framework import serializers


class SaleSerializer(serializers.ModelSerializer):
    sell_time = serializers.SerializerMethodField()

    class Meta:
        model = models.SalesInfo
        fields = '__all__'
        # depth = 1

    def get_sell_time(self, row):
        if row.sell_time is None:
            return None
        return row.sell_time.strftime('%Y-%m-%d %H:%M:%S')
