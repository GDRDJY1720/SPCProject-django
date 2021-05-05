# _*_ coding:utf-8 _*_

import time
import datetime
import json

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from commonTool import ali_api, tool
from utils.pagination import CommonPagination
from api.utils import serializers
from device import models as Dmodels
from product import models as Pmodels
from account import models as Umodels
from account.tool import account


class UserView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        tmp = serializers.UserSerializer(data=request.data, context={'user': None})
        if tmp.is_valid():
            # 创建token
            user = tmp.context['user']
            stime = time.time()
            now = datetime.datetime.now()
            token_obj = Umodels.UserToken.objects.filter(user_id=user.id).first()
            if token_obj is None or now > token_obj.end_time:
                time_out = now + datetime.timedelta(days=1)
                m = account.md5(user.phonenum, stime)
                Umodels.UserToken.objects.update_or_create(user=user,
                                                           defaults={'start_time': now,
                                                                     'token': m,
                                                                     'end_time': time_out})
            else:
                m = token_obj.token
            # 返回
            res['token'] = m
            return Response(res)
        else:
            res['code'] = tmp.errors.get('non_field_errors')[0].code
            res['msg'] = tmp.errors.get('non_field_errors')[0]
            return Response(res)


class QueryDeviceList(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliDeviceAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        if request.user.from_privilege == 1:
            param = {}
        else:
            param = {'from_user_id': request.user.id}

        iot_list = Dmodels.Device.objects.filter(**param).order_by('id').values_list('iot_id', flat=True)
        if not iot_list:
            res['data'] = []
            res['count'] = 0
            return Response(res)

        pager = self.paginate_queryset(iot_list)
        state_dic = self.get_api_run(res=res, api_name='BatchGetDeviceState', IotId_list=pager)
        if res['code'] != 1000:
            return Response(res)

        status_list = state_dic.get('DeviceStatusList').get('DeviceStatus')

        device_list = Dmodels.Device.objects.filter(iot_id__in=iot_list)
        ser = self.get_serializer(instance=device_list, many=True, context={'status': status_list})
        res['data'] = ser.data
        return Response(res)


class QueryPropertyList(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        # 这里可以改成动态参数查询 4-19
        product_key = request.data.get('productKey', None)
        if not product_key:
            res['code'] = 1050
            res['msg'] = 'productKey参数未找到'
            return Response(res)

        # device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
        product = Pmodels.Product.objects.filter(productkey=product_key).first()
        if not product:
            res['code'] = 1051
            res['msg'] = '产品不存在，请检查productKey是否正确'
            return Response(res)
        dic = self.get_api_run(api_name='QueryThingModel', res=res, ProductKey=product.productkey)
        if res['code'] != 1000:
            return Response(res)

        res['data'] = {
            'productName': product.productname,
            'productKey': product.productkey,
            'properties': self.get_property_info(json.loads(dic.get('Data').get('ThingModelJson')))
        }
        return Response(res)

    @staticmethod
    def get_property_info(data: dict) -> list:
        identifier_list = ['Voltage', 'Speed', 'Current', 'Torque', 'Error', 'TotalOutput', 'TotalRunTime',
                           'CellSignalStrength', 'SRuntime', 'Latitude', 'Longitude']
        tmp_data = data.get('properties')
        # print(tmp_data)
        result = []

        for d in tmp_data:
            if d.get('identifier', None)[:-2] not in identifier_list and d.get('identifier',
                                                                               None) not in identifier_list:
                output_data = {
                    'name': d.get('name'),
                    'identifier': d.get('identifier'),
                    'unit': d.get('dataSpecs').get('unit'),
                    'max': d.get('dataSpecs').get('max'),
                    'min': d.get('dataSpecs').get('min'),
                    'step': d.get('dataSpecs').get('step')
                }
                result.append(output_data)

        return result


class SetProperty(GenericAPIView, ali_api.APIRun):
    """
    设置单条属性
    """
    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        device_secret = request.data.get('deviceSecret', None)
        item = request.data.get('items', None)
        if item is None:
            res['code'] = 1050
            res['msg'] = 'items参数缺失'
            return Response(res)

        try:
            items = json.dumps(item)
        except Exception:
            res['code'] = 1051
            res['msg'] = 'items参数错误，格式为{"key": value}，其中key为属性的identifier'
            return Response(res)

        device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
        if not device:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        self.get_api_run(res=res, api_name='SetDeviceProperty', Items=items, IotId=device.iot_id)
        if res['code'] != 1000:
            return Response(res)

        return Response(res)


class SetTask(GenericAPIView, ali_api.APIRun):
    """
    设置多条属性
    """
    serializer_class = serializers.SetPropertiesSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        device_secret = request.data.get('deviceSecret', None)
        task_id = request.data.get('TaskID', None)
        item = request.data.get('items', None)

        if device_secret is None:
            res['code'] = 1050
            res['msg'] = 'deviceSecret参数缺失'
            return Response(res)

        if task_id is None:
            res['code'] = 1050
            res['msg'] = 'taskId参数缺失'
            return Response(res)

        if item is None:
            res['code'] = 1050
            res['msg'] = 'items参数缺失'
            return Response(res)

        try:
            task = int(task_id)
        except Exception:
            res['code'] = 1049
            res['msg'] = 'taskId参数错误'
            return Response(res)

        try:
            item['TaskId'] = task
            item['TaskFlag'] = 0
            items = json.dumps(item)
        except Exception:
            res['code'] = 1051
            res['msg'] = 'items参数错误，格式为{"key": value, "key1": value1...}，其中key为属性的identifier'
            return Response(res)

        device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
        if not device:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        self.get_api_run(res=res, api_name='SetDevicesProperty', Items=items, ProductKey=device.from_product.productkey,
                         DeviceNameList=[device.device_name, ])
        if res['code'] != 1000:
            return Response(res)
        # res['data'] = items

        return Response(res)


class QueryProductList(GenericAPIView):
    serializer_class = serializers.QueryProductListSerializer
    pagination_class = CommonPagination

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        if request.user.from_privilege == 1:
            product_list = Pmodels.Product.objects.order_by('id').all()
        else:
            product_list = request.user.from_product.all().order_by('id')

        pager = self.paginate_queryset(product_list)
        ser = self.get_serializer(instance=pager, many=True)

        res['data'] = ser.data
        return Response(res)
