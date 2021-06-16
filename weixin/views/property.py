# _*_ coding:utf-8 _*_

import json
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from commonTool import ali_api
from weixin.utils import serializer
from utils.pagination import CommonPagination
from device import models as Dmodels


class WXPropertyView(GenericAPIView, ali_api.APIRun):
    authentication_classes = []
    serializer_class = serializer.QueryPropertySerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        device_id = request.data.get('id', None)
        if not device_id:
            res['code'] = 1050
            res['msg'] = 'device_secret参数未找到'
            return Response(res)

        device_obj = Dmodels.Device.objects.filter(id=device_id).first()
        dic = self.get_api_run(api_name='QueryThingModel', res=res, ProductKey=device_obj.fk_product.product_key)
        if res['code'] != 1000:
            return Response(res)

        ser = self.get_serializer(instance=device_obj,
                                  context={'data': self.get_property_info(
                                      json.loads(dic.get('Data').get('ThingModelJson')))})

        res['data'] = ser.data
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
                    'dataSpecs': d.get('dataSpecs'),
                    'rwFlag': d.get('rwFlag'),
                }
                result.append(output_data)

        return result


class WXSetProperties(GenericAPIView, ali_api.APIRun):
    authentication_classes = []
    serializer_class = None
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        device_id = request.data.get('deviceId', None)
        items = json.dumps(request.data.get('items', None))

        device_obj = Dmodels.Device.objects.filter(id=device_id).first()
        if not device_obj:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        self.get_api_run(res=res, api_name='SetDevicesProperty', Items=items,
                         ProductKey=device_obj.fk_product.product_key,
                         DeviceNameList=[device_obj.device_name, ])
        if res['code'] != 1000:
            return Response(res)

        res['data'] = items
        return Response(res)
