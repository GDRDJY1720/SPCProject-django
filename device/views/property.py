# _*_ coding:utf-8 _*_

import json
import time

from commonTool import ali_api, tool
from device import models
from product import models as Pmodels
from device.utils.serializer import SetPropertySerializer, PropertySerializer
from utils.pagination import CommonPagination

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class PropertyInfoView(GenericViewSet, ali_api.APIRun):
    queryset = models.Device.objects.all()
    serializer_class = PropertySerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        # 设备id
        pk = kwargs.get('pk', None)

        device = models.Device.objects.filter(id=pk).first()

        dic = self.get_api_run(api_name='QueryThingModel', res=res, ProductKey=device.from_product.productkey)
        if res['code'] != 1000:
            return Response(res)

        if not device.from_product.product_servo_num:
            servo_dic = self.get_api_run(api_name='ListProductTags', res=res, ProductKey=device.from_product.productkey)
            if res['code'] != 1000:
                return Response(res)

            try:
                servo_num = int(servo_dic.get('Data').get('ProductTag')[0].get('TagValue'))
                Pmodels.Product.objects.filter(id=device.from_product_id).update(product_servo_num=servo_num)
            except Exception:
                res['code'] = 1015
                res['msg'] = '伺服数量未设置，无法查询对应属性'
                return Response(res)
        else:
            servo_num = int(device.from_product.product_servo_num)

        data = self.get_property_info(data=json.loads(dic.get('Data').get('ThingModelJson')), servo_num=servo_num)
        ser = self.get_serializer(instance=device, context={'request': request, 'data': data, 'servo_num': servo_num})

        res['data'] = ser.data
        return Response(res)

    def data(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        pk = kwargs.get('pk', None)
        identifier = request.data.get('identifier', None)
        history = request.data.get('history', False)

        device = models.Device.objects.filter(id=pk).first()

        # 这里会根据方法名来判断startTime和endTime哪个大哪个小
        # 在相同排序和时间下，两个方法的起始和结束时间是反的!!!!
        tmp_time = time.time()
        if type(identifier) is str:
            api_name = 'QueryDevicePropertyData'
            tmp_starttime = str(round(tmp_time * 1000) - 60000)
            tmp_endtime = str(round(tmp_time * 1000))
            in_start_time = request.data.get('startTime', None)
            in_end_time = request.data.get('endTime', None)
            page_size = 50
        elif type(identifier) is list:
            api_name = 'QueryDevicePropertiesData'
            tmp_endtime = str(round(tmp_time * 1000) - 60000)
            tmp_starttime = str(round(tmp_time * 1000))
            in_end_time = request.data.get('startTime', None)
            in_start_time = request.data.get('endTime', None)
            page_size = 100
        else:
            res['code'] = 1020
            return Response(res)

        if history:
            if not (in_start_time and in_end_time):
                res['code'] = 1016
                res['msg'] = '历史记录查询的起始和结束时间不能为空'
                return Response(res)

            starttime = in_start_time
            endtime = in_end_time
        else:
            starttime = tmp_starttime
            endtime = tmp_endtime
            page_size = 5

        res_data = []
        if len(identifier) > 10:
            dic = {}
            for j in range(len(identifier) // 10 + 1):
                if j == len(identifier) - 1:
                    tmp_list = identifier[j * 10:]
                else:
                    tmp_list = identifier[j * 10:(j + 1) * 10]

                dic = self.get_api_run(api_name=api_name, res=res,
                                       StartTime=starttime,
                                       Identifier=tmp_list,
                                       Asc=0,
                                       EndTime=endtime,
                                       PageSize=page_size,
                                       ProductKey=device.from_product.productkey,
                                       DeviceName=device.device_name)
                if res['code'] != 1000:
                    return Response(res)

                res_data += dic.get('PropertyDataInfos').get('PropertyDataInfo')
        else:
            dic = self.get_api_run(api_name=api_name, res=res,
                                   StartTime=starttime,
                                   Identifier=identifier,
                                   Asc=0,
                                   EndTime=endtime,
                                   PageSize=page_size,
                                   ProductKey=device.from_product.productkey,
                                   DeviceName=device.device_name)
            if res['code'] != 1000:
                return Response(res)
            res_data = dic.get('PropertyDataInfos').get('PropertyDataInfo')

        if api_name == 'QueryDevicePropertyData':
            res['data'] = dic.get('Data')
        else:
            res['data'] = res_data

        print(res['data'], api_name)

        return Response(res)

    @staticmethod
    def get_property_info(data: dict, servo_num: int):
        tmp = ['Voltage', 'Speed', 'Current', 'Torque']
        result = {}

        tmp_data = data.get('properties')

        for i in range(1, servo_num + 1):
            identifier_list = [j + '_' + str(i) for j in tmp]

            for d in tmp_data:
                if d.get('identifier', None) in identifier_list:
                    servo_name = d.get('name').split('伺服')[0] + '伺服'
                    output_data = {
                        'name': d.get('name'),
                        'identifier': d.get('identifier'),
                        'unit': tool.unit_custom(d.get('name')[-2:]),
                        'max': d.get('dataSpecs').get('max'),
                        'min': d.get('dataSpecs').get('min'),
                        'step': d.get('dataSpecs').get('step')
                    }
                    try:
                        result[servo_name].append(output_data)
                    except KeyError:
                        result[servo_name] = []
                        result[servo_name].append(output_data)

        return result


class SetPropertyView(GenericViewSet, ali_api.APIRun):
    queryset = models.Device.objects.all()
    serializer_class = SetPropertySerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        product_id = request.query_params.get('productID', None)
        if not product_id:
            res['code'] = 1050
            res['msg'] = 'productID参数缺失'
            return Response(res)
        print(product_id)

        product_obj = Pmodels.Product.objects.filter(id=product_id).first()
        dic = self.get_api_run(api_name='QueryThingModel', res=res, ProductKey=product_obj.productkey)
        if res['code'] != 1000:
            return Response(res)

        ser = self.get_serializer(instance=product_obj,
                                  context={'data': self.get_property_info(
                                      json.loads(dic.get('Data').get('ThingModelJson')))})

        res['data'] = ser.data
        return Response(res)

    def set(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        device_id = request.data.get('deviceID', None)
        items = json.dumps(request.data.get('items', None))

        device_obj = models.Device.objects.filter(id=device_id).first()
        if not device_obj:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        self.get_api_run(res=res, api_name='SetDevicesProperty', Items=items,
                         ProductKey=device_obj.from_product.productkey,
                         DeviceNameList=[device_obj.device_name, ])
        if res['code'] != 1000:
            return Response(res)

        return Response(res)

    @staticmethod
    def get_property_info(data: dict) -> list:
        identifier_list = ['left_length', 'right_length', 'left_angle', 'right_angle', 'length', 'angle']
        tmp_data = data.get('properties')
        result = []

        for d in tmp_data:
            if d.get('identifier', None)[:-3] in identifier_list:
                output_data = {
                    'name': d.get('name'),
                    'identifier': d.get('identifier'),
                    'dataSpecs': d.get('dataSpecs'),
                    'rwFlag': d.get('rwFlag'),
                }
                result.append(output_data)

        return result
