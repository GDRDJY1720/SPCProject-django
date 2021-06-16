# _*_ coding:utf-8 _*_

import json
import datetime
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from commonTool import ali_api
from weixin.utils import serializer
from utils.pagination import CommonPagination
from sale import models
from device import models as Dmodels


class WXSaleView(GenericViewSet, ali_api.APIRun):

    def create(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        params = {}

        device_id = request.data.get('deviceId', None)
        if device_id is None:
            res['code'] = 1050
            res['msg'] = 'deviceId参数缺失'
            return Response(res)

        device_obj = Dmodels.Device.objects.filter(id=device_id)
        if device_obj.first() is None:
            res['code'] = 1049
            res['msg'] = '设备不存在'
            return Response(res)

        customer_code = request.data.get('customer_code', None)
        # 销售时间接收的是时间戳
        sell_time = request.data.get('sell_time', None)
        if sell_time is None:
            res['code'] = 1050
            res['msg'] = 'sell_time参数缺失'
            return Response(res)
        sell_time = int(sell_time)

        sell_code = request.data.get('sell_code', None)
        sell_site = request.data.get('sell_site', None)
        company_name = request.data.get('company_name', None)

        if customer_code:
            params['customer_code'] = customer_code
        else:
            res['code'] = 1050
            res['msg'] = 'customer_code参数缺失'
            return Response(res)
        if sell_time:
            params['sell_time'] = datetime.datetime.fromtimestamp(sell_time)
        if sell_code:
            params['sell_code'] = sell_code
        if sell_site:
            params['sell_site'] = sell_site
        if company_name:
            params['company_name'] = company_name

        try:
            sale_obj = models.SalesInfo.objects.create(**params)
            device_obj.update(fk_sales=sale_obj)
        except Exception as e:
            print(e)
            res['code'] = 1010
            res['msg'] = '添加错误'
            return Response(res)

        return Response(res)

    def update_info(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        params = {}

        device_id = kwargs.get('sign')

        customer_code = request.data.get('customer_code', None)
        if customer_code is None:
            res['code'] = 1050
            res['msg'] = 'customer_code参数缺失'
            return Response(res)
        params['customer_code'] = customer_code

        params['company_name'] = request.data.get('company_name', None)

        sell_time = request.data.get('sell_time', None)
        if sell_time is not None:
            sell_time = int(sell_time)
            params['sell_time'] = datetime.datetime.fromtimestamp(sell_time)
        else:
            res['code'] = 1050
            res['msg'] = 'sell_time参数缺失'
            return Response(res)

        params['sell_code'] = request.data.get('sell_code', None)
        params['sell_site'] = request.data.get('sell_site', None)

        device_obj = Dmodels.Device.objects.filter(id=device_id).first()
        if device_obj is None:
            res['code'] = 1049
            res['msg'] = '设备不存在'
            return Response(res)

        models.SalesInfo.objects.filter(id=device_obj.fk_sales_id).update(**params)

        return Response(res)
