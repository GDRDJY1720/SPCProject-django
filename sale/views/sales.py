# _*_ coding:utf-8 _*_
import json
import datetime

from commonTool import ali_api
from sale import models
from sale.utils import serializer
from utils.pagination import CommonPagination
from device import models as Dmodels
from product import models as Pmodels
from account import models as Umodels

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class SalesInfo(GenericViewSet):
    queryset = models.SalesInfo.objects.all()
    serializer_class = serializer.SaleSerializer
    pagination_class = CommonPagination

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        sales_list = models.SalesInfo.objects.all()
        sale_pager = self.paginate_queryset(sales_list)
        sale_ser = self.get_serializer(sale_pager, many=True)

        res['data'] = sale_ser.data
        return Response(res)

    def list_limit(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        params = {}

        sign = kwargs.get('sign')
        if sign == 'code':
            data = request.query_params.get('data', None)
            if data is None:
                res['code'] = 1050
                res['msg'] = 'code参数缺失'
                return Response(res)
            params['customer_code'] = data

        sales_list = models.SalesInfo.objects.filter(**params)
        sale_pager = self.paginate_queryset(sales_list)
        sale_ser = self.get_serializer(sale_pager, many=True)

        res['data'] = sale_ser.data
        return Response(res)

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
        sell_time = int(request.data.get('sell_time', None)) / 1000
        sell_code = request.data.get('sell_code', None)
        sell_site = request.data.get('sell_site', None)

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

        try:
            sale_obj = models.SalesInfo.objects.create(**params)
            device_obj.update(fk_sales=sale_obj)
        except Exception as e:
            print(e)
            res['code'] = 1010
            res['msg'] = '添加错误'
            return Response(res)

        return Response(res)

    def destroy(self, request, *args, **kwargs):
        """
        应该在删除之前，检查这个订单下面还有没有设备，如果没有就直接删除订单
        :return:
        """
        res = {'code': 1000, 'msg': ''}

        device_id = request.data.get('deviceId', None)
        if device_id is None:
            res['code'] = 1050
            res['msg'] = 'deviceId参数缺失'
            return Response(res)

        Dmodels.Device.objects.filter(id=device_id).update(fk_sales=None)

        return Response(res)

    def update(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        sell_id = request.data.get('sellId', None)
        if sell_id is None:
            res['code'] = 1050
            res['msg'] = 'sellId参数缺失'
            return Response(res)

        device_id = request.data.get('deviceId', None)
        if device_id is None:
            res['code'] = 1050
            res['msg'] = 'deviceId参数缺失'
            return Response(res)

        sale_obj = models.SalesInfo.objects.filter(id=sell_id).first()
        if sale_obj is None:
            res['code'] = 1049
            res['msg'] = '无订单信息'
            return Response(res)

        device_obj = Dmodels.Device.objects.filter(id=device_id)
        if device_obj.first() is None:
            res['code'] = 1049
            res['msg'] = '设备不存在'
            return Response(res)

        device_obj.update(fk_sales=sale_obj)
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

        sell_time = int(request.data.get('sell_time', None)) / 1000
        if sell_time:
            params['sell_time'] = datetime.datetime.fromtimestamp(sell_time)
        params['sell_code'] = request.data.get('sell_code', None)
        params['sell_site'] = request.data.get('sell_site', None)

        device_obj = Dmodels.Device.objects.filter(id=device_id).first()
        if device_obj is None:
            res['code'] = 1049
            res['msg'] = '设备不存在'
            return Response(res)

        models.SalesInfo.objects.filter(id=device_obj.fk_sales_id).update(**params)

        return Response(res)
