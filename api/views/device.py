# _*_ coding:utf-8 _*_
import json

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from commonTool import ali_api
from utils.pagination import CommonPagination
from api.utils import serializers
from device import models as Dmodels


class QueryDeviceListView(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliDeviceAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        if request.user.fk_customer:
            param = {'fk_user_id': request.user.id}
        else:
            param = {}

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


class StartDeviceView(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        """
        用于远程启动设备
        :param request: 请求信息
        :param args: 请求参数
        :param kwargs: 请求参数
        :return: 返回状态信息
        """
        res = {"code": 1000, "msg": ""}

        # 判断是否有远程操作的权限
        if request.user.remote_control:
            # 查询要操作的设备是否存在
            device_secret = request.data.get('deviceSecret', None)
            if device_secret is None:
                res['code'] = 1050
                res['msg'] = 'deviceSecret参数缺失'
                return Response(res)

            device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
            if not device:
                res['code'] = 1010
                res['msg'] = '设备不存在'
                return Response(res)

            # 如果有操作权限，则下发属性至阿里云，远程操作设备启动
            self.get_api_run(api_name="SetDevicesProperty", res=res, Items=json.dumps({"startDevice": 1}),
                             ProductKey=device.fk_product.product_key, DeviceNameList=[device.device_name])
            if res['code'] != 1000:
                return Response(res)

            res["msg"] = "启动信号下发成功"

            # 返回状态
            return Response(res)
        else:
            res["code"] = 1015
            res["msg"] = "无远程操作权限，请联系厂家开启"
            return Response(res)


class StopDeviceView(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        """
        用于远程停止设备
        :param request: 请求信息
        :param args: 请求参数
        :param kwargs: 请求参数
        :return: 返回状态信息
        """
        res = {"code": 1000, "msg": ""}

        # 判断是否有远程操作的权限
        if request.user.remote_control:
            # 查询要操作的设备是否存在
            device_secret = request.data.get('deviceSecret', None)
            if device_secret is None:
                res['code'] = 1050
                res['msg'] = 'deviceSecret参数缺失'
                return Response(res)

            device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
            if not device:
                res['code'] = 1010
                res['msg'] = '设备不存在'
                return Response(res)

            # 如果有操作权限，则下发属性至阿里云，远程操作设备停止
            self.get_api_run(api_name="SetDevicesProperty", res=res, Items=json.dumps({"stopDevice": 1}),
                             ProductKey=device.fk_product.product_key, DeviceNameList=[device.device_name])
            if res['code'] != 1000:
                return Response(res)

            res["msg"] = "停止信号下发成功"

            # 返回状态
            return Response(res)
        else:
            res["code"] = 1015
            res["msg"] = "无远程操作权限，请联系厂家开启"
            return Response(res)


class PauseDeviceView(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.QueryDeviceListSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        """
        用于远程暂停设备
        :param request: 请求信息
        :param args: 请求参数
        :param kwargs: 请求参数
        :return: 返回状态信息
        """
        res = {"code": 1000, "msg": ""}

        # 判断是否有远程操作的权限
        if request.user.remote_control:
            # 查询要操作的设备是否存在
            device_secret = request.data.get('deviceSecret', None)
            if device_secret is None:
                res['code'] = 1050
                res['msg'] = 'deviceSecret参数缺失'
                return Response(res)

            device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
            if not device:
                res['code'] = 1010
                res['msg'] = '设备不存在'
                return Response(res)

            # 如果有操作权限，则下发属性至阿里云，远程操作设备暂停
            self.get_api_run(api_name="SetDevicesProperty", res=res, Items=json.dumps({"pauseDevice": 1}),
                             ProductKey=device.fk_product.product_key, DeviceNameList=[device.device_name])
            if res['code'] != 1000:
                return Response(res)

            res["msg"] = "暂停信号下发成功"

            # 返回状态
            return Response(res)
        else:
            res["code"] = 1015
            res["msg"] = "无远程操作权限，请联系厂家开启"
            return Response(res)
