# _*_ coding:utf-8 _*_

import requests
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from commonTool import ali_api
from weixin.utils import serializer
from utils.pagination import CommonPagination
from device import models as Dmodels
from account import models as Umodels


class WXDeviceInfoView(GenericViewSet, ali_api.APIRun):
    authentication_classes = []
    serializer_class = serializer.QueryDeviceSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliDeviceAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        actual_device_secret = request.data.get('deviceSecret', None)
        module_secret = request.data.get('moduleSecret', None)

        if actual_device_secret is None and module_secret is None:
            res['code'] = 1050
            res['msg'] = '参数缺失'
            return Response(res)

        device_obj = Dmodels.Device.objects.filter(actual_device_secret=actual_device_secret, module_secret=module_secret).first()
        dic = self.get_api_run(api_name='GetDeviceStatus', res=res, IotId=device_obj.iot_id)
        if res['code'] != 1000:
            return Response(res)

        ser = self.get_serializer(instance=device_obj, context={'status': dic.get('Data').get('Status')})
        res['data'] = ser.data
        return Response(res)

    def update(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        pk = kwargs.get('pk', None)

        device = Dmodels.Device.objects.filter(id=pk).first()
        if not device:
            res['code'] = 1014
            res['msg'] = '设备不存在'
            return Response(res)

        print(request.data)

        return Response(res)
