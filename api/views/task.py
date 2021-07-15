# _*_ coding:utf-8 _*_

import json

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from commonTool import ali_api, tool
from utils.pagination import CommonPagination
from api.utils import serializers
from device import models as Dmodels
from product import models as Pmodels
from api import models as Tmodels


class QueryPropertyListView(GenericAPIView, ali_api.APIRun):
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
        product = Pmodels.Product.objects.filter(product_key=product_key).first()
        if not product:
            res['code'] = 1051
            res['msg'] = '产品不存在，请检查productKey是否正确'
            return Response(res)
        dic = self.get_api_run(api_name='QueryThingModel', res=res, ProductKey=product.product_key)
        if res['code'] != 1000:
            return Response(res)

        res['data'] = {
            'productName': product.product_name,
            'productKey': product.product_key,
            'properties': self.get_property_info(json.loads(dic.get('Data').get('ThingModelJson')))
        }
        return Response(res)

    @staticmethod
    def get_property_info(data: dict) -> list:
        identifier_list = ['left_length', 'right_length', 'left_angle', 'right_angle', 'length', 'angle']
        other_ident = ['TaskNum', 'NumberRoots']
        tmp_data = data.get('properties')
        # print(tmp_data)
        result = []

        for d in tmp_data:
            if d.get('identifier', None)[:-3] in identifier_list or d.get('identifier', None) in other_ident:
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


class SetPropertyView(GenericAPIView, ali_api.APIRun):
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


class SetTaskView(GenericAPIView, ali_api.APIRun):
    """
    设置多条属性
    """
    serializer_class = serializers.SetPropertiesSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        params = {}

        device_secret = request.data.get('deviceSecret', None)
        task_id = request.data.get('taskID', None)
        item = request.data.get('items', None)
        task_info = request.data.get('taskInfo', None)
        task_submit_url = request.data.get('submitUrl', None)
        task_submit_info = request.data.get('submitInfo', None)

        # 参数传入验证及基本处理
        if device_secret is None:
            res['code'] = 1050
            res['msg'] = 'deviceSecret参数缺失'
            return Response(res)

        device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
        if not device:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        device_api = ali_api.APIRun()
        device_api.Api = ali_api.AliDeviceAPI()
        dic = device_api.get_api_run(res=res, api_name="GetDeviceStatus", IotId=device.iot_id)
        if res['code'] != 1000:
            return Response(res)

        if dic.get("Data").get("Status") != "ONLINE":
            res['code'] = 1053
            res['msg'] = "设备未处于在线状态，禁止下载任务"
            return Response(res)

        if item is None:
            res['code'] = 1050
            res['msg'] = 'items参数缺失'
            return Response(res)

        try:
            item['TaskStatus'] = 0
            items = json.dumps(item)
        except Exception:
            res['code'] = 1051
            res['msg'] = 'items参数错误，格式为{"key": value, "key1": value1...}，其中key为属性的identifier'
            return Response(res)

        if type(task_submit_info) != list:
            res['code'] = 1051
            res['msg'] = 'submitInfo的类型为Array类型，请确认类型后重新输入'
            return Response(res)

        if task_submit_info is not None and task_submit_url is None:
            res['code'] = 1050
            res['msg'] = '请指定提交URL'
            return Response(res)

        if task_submit_info is not None and task_info is None:
            res['code'] = 1050
            res['msg'] = 'taskInfo参数缺失，当有submitInfo参数的时候，taskInfo参数为必填项'
            return Response(res)

        if task_submit_info:
            for info in task_submit_info:
                if info not in task_info.keys():
                    res['code'] = 1052
                    res['msg'] = 'submitInfo中的值需要与taskInfo参数中的key值对应'
                    return Response(res)

        # 添加任务的提交地址以及提交信息字段，同时在任务信息有下发请求的时候，存储任务编号，任务其他信息等基本任务信息 5-10
        if task_id:
            params['task_id'] = task_id

        if task_info:
            params['task_info'] = json.dumps(task_info)
            # params['task_info'] = task_info
            # print(params['task_info'], type(params['task_info']))

        if task_submit_url:
            params['task_submit_url'] = task_submit_url

        if task_submit_info:
            params['task_submit_info'] = json.dumps(task_submit_info)

        if task_info or task_id or task_submit_url:
            try:
                Tmodels.Task.objects.update_or_create(fk_device=device, defaults=params)
            except Exception as e:
                print(e)
                res['code'] = 1050
                res['msg'] = '参数有错误，请检查参数合法性'
                return Response(res)

        # 下发任务信息
        self.get_api_run(res=res, api_name='SetDevicesProperty', Items=items,
                         ProductKey=device.fk_product.product_key,
                         DeviceNameList=[device.device_name, ])
        if res['code'] != 1000:
            return Response(res)
        # res['data'] = items

        return Response(res)
