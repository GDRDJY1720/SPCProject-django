# _*_ coding:utf-8 _*_

import json
import time

from django.conf import settings

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


class V2QueryPropertyListView(GenericAPIView, ali_api.APIRun):
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

        # 获取标签中的长度角度等属性的数量的字典（长度角度的定义为约定）
        test = self.get_api_run(api_name="ListProductTags", res=res, ProductKey=product.product_key)

        # 如果获取成功，将获取的信息通过固定方法进行组合成为新的返回
        properties = self.get_property_number(test)

        # 返回新的字典
        res["data"] = {
            'productName': product.product_name,
            "properties": properties
        }

        return Response(res)

    @staticmethod
    def get_property_info(data: dict) -> list:
        identifier_list = settings.TASK_BASICS_PROPERTIES
        other_ident = settings.TASK_OTHER_PROPERTIES
        tmp_data = data.get('properties')
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

    def get_property_number(self, data: dict) -> list:
        res = []
        if data is None:
            return []

        property_list = data.get("Data").get("ProductTag")
        if property_list is None or len(property_list) == 0:
            return []

        for i in property_list:
            if i["TagKey"] in settings.TASK_BASICS_PROPERTIES:
                res.append({
                    "key": i["TagKey"],
                    "type": "List",
                    "maxLength": i["TagValue"]
                })

        # 将非基础属性添加到返回信息中
        for i in settings.TAG_TASK_PROPERTIES:
            res.append({
                "key": i,
                "type": "Int"
            })

        return res


class V2SetTaskView(GenericAPIView, ali_api.APIRun):
    """
    设置多条属性
    """
    serializer_class = serializers.SetPropertiesSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        """
        用于下发任务
        :param request: 用户请求信息
        :param args:  请求参数
        :param kwargs: 请求参数
        :rtype: Response
        """
        res = {'code': 1000, 'msg': ''}

        # 校验传入的参数正确性
        params = self.get_verify_params(request, res)

        # 将items参数转化为阿里云平台能够识别的参数格式
        if type(params) is not Response:
            items = self.get_items(res, params["item"])
        else:
            return params

        # 下发任务到阿里云平台
        self.get_api_run(res=res, api_name='SetDevicesProperty', Items=items,
                         ProductKey=params["device"].fk_product.product_key,
                         DeviceNameList=[params["device"].device_name, ])
        if res['code'] != 1000:
            return Response(res)

        # 如果下发成功，则存储任务信息到数据库
        self.get_db_task(res, params)

        # 返回任务下发状态
        return Response(res)

    def get_verify_params(self, request, res: dict) -> (Response, dict):
        """
        用于检查参数的正确性
        item: {
            AL: [...,0],
            count: xx
        }
        :param request:
        :param res: 传入的返回字典
        :return:
        """
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

        if task_id is None:
            res['code'] = 1050
            res['msg'] = 'taskID参数缺失'
            return Response(res)

        device = Dmodels.Device.objects.filter(actual_device_secret=device_secret).first()
        if not device:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        # 测试时暂时注释
        device_api = ali_api.APIRun()
        device_api.Api = ali_api.AliDeviceAPI()
        dic = device_api.get_api_run(res=res, api_name="GetDeviceStatus", IotId=device.iot_id)
        if res['code'] != 1000:
            return Response(res)

        if dic.get("Data").get("Status") != "ONLINE":
            res['code'] = 1053
            res['msg'] = "设备未处于在线状态，禁止下载任务"
            return Response(res)

        # 检查任务的下发属性是否存在
        if item is None:
            res['code'] = 1050
            res['msg'] = 'items参数缺失'
            return Response(res)

        # 校验任务的下发属性与设备是否匹配
        task_property = []
        dic = self.get_api_run(api_name="ListProductTags", res=res, ProductKey=device.fk_product.product_key)
        if res['code'] != 1000:
            return Response(res)
        for i in dic["Data"]["ProductTag"]:
            task_property.append(i.get("TagKey"))

        for k in item.keys():
            if k not in settings.TAG_TASK_PROPERTIES and k not in task_property:
                res['code'] = 1050
                res['msg'] = '任务参数与设备不匹配，请检查后重新提交'
                return Response(res)

        # 检测任务的提交信息
        if task_submit_info is not None and type(task_submit_info) != list:
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

        return {
            "device": device,
            "task_id": task_id,
            "item": item,
            "task_info": task_info,
            "task_submit_url": task_submit_url,
            "task_submit_info": task_submit_info
        }

    @staticmethod
    def get_items(res, item):
        """
        items ={
          leftAngle: [],
          leftLength: [],
          rightAngle: [],
          rightLength: [],
          count: 4,
          diameter: 8
        }
        :param res: 返回结果字典
        :param item: 任务属性
        :return: 拼接好的任务属性
        """

        result = {}

        if item is None:
            res['code'] = 1050
            res['msg'] = 'items参数缺失'
            return Response(res)

        # 循环提取item中的每一项value
        for key in item:
            for index, value in enumerate(item[key]):
                # 循环期间，key后面加'_${index}',组合阿里匹配的任务字符串
                result[key + "_" + (str(index + 1) if index + 1 > 9 else "0" + str(index + 1))] = value

        # 返回该字符串
        return result

    @staticmethod
    def get_db_task(res: dict, param: dict):
        device = param["device"]
        param.pop("device")
        param.pop("item")
        try:
            Tmodels.Task.objects.update_or_create(fk_device=device, defaults=param)
        except Exception as e:
            print(e)
            res['code'] = 1050
            res['msg'] = '参数有错误，请检查参数合法性'
            return Response(res)


class V2QueryDeviceTaskView(GenericAPIView, ali_api.APIRun):
    serializer_class = serializers.SetPropertiesSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def post(self, request, *args, **kwargs):
        res = {"code": 1000, "msg": ""}

        # 校验参数的正确性
        params = self.get_verify_params(request, res)

        # 如果参数正确通过标签获取要查询的属性名
        if type(params) is not Response:
            self.get_properties(res, params)
        else:
            return params

        # 调用阿里云平台查询属性接口查询指定属性,调用接口QueryDevicePropertiesData
        tmp_time = time.time()
        endTime = str(round(tmp_time * 1000) - 60000 * 60 * 24)
        startTime = str(round(tmp_time * 1000))
        res_data = []
        if len(params["items"]) > 10:
            for j in range(len(params["items"]) // 10 + 1):
                if j == len(params["items"]) - 1:
                    tmp_list = params["items"][j * 10:]
                else:
                    tmp_list = params["items"][j * 10:(j + 1) * 10]

                dic = self.get_api_run(api_name="QueryDevicePropertiesData", res=res,
                                       StartTime=startTime,
                                       Identifier=tmp_list,
                                       Asc=0,
                                       EndTime=endTime,
                                       PageSize=2,
                                       ProductKey=params["device"].fk_product.product_key,
                                       DeviceName=params["device"].device_name)
                if res['code'] != 1000:
                    return Response(res)

                res_data += dic.get('PropertyDataInfos').get('PropertyDataInfo')

        # 将查询到的属性组合成易识别格式（数组）
        res["data"] = self.get_current_task(res_data, params)

        # 返回查询的数据给调用方
        return Response(res)

    @staticmethod
    def get_verify_params(request, res: dict) -> (Response, dict):
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

        return {
            "device": device
        }

    def get_properties(self, res, params):
        result = []

        # 获取标签
        dic = self.get_api_run(api_name="ListProductTags", res=res, ProductKey=params["device"].fk_product.product_key)
        if res['code'] != 1000:
            return Response(res)

        # 循环标签生成要查询的属性标识符
        for i in dic["Data"]["ProductTag"]:
            if i["TagKey"] != "servo":
                tmp = i["TagKey"][0:1].capitalize() + i["TagKey"][1:]
                for j in range(1, int(i["TagValue"]) + 1):
                    result.append("current" + tmp + "_" + (str(j) if j > 9 else "0" + str(j)))

        # 添加额外需要查询的属性
        for i in settings.TASK_QUERY_PROPERTIES:
            result.append("current" + i[0:1].capitalize() + i[1:])

        # 添加到params中
        params["items"] = result
        params["task_property"] = dic["Data"]["ProductTag"]

    @staticmethod
    def get_current_task(task: list, params: dict) -> dict:
        """
        用于转化获取的属性参数为指定的格式
        :param task: 任务属性列表
        :param params: 需要的参数
        :return: 返回转化结果
        """
        result = {}

        # 根据标签生成对应的字典，数组中填出对应的数量，值都为0
        for i in params["task_property"]:
            if i["TagKey"] != "servo":
                result[i["TagKey"]] = [0 for x in range(0, int(i["TagValue"]))]

        for j in settings.TASK_QUERY_PROPERTIES:
            result[j] = 0

        # 扫描任务属性列表，每遇到一个就从名称中提取出下标
        for i in task:
            # 检查是否有属性，如果没有属性就不变
            if len(i["List"]["PropertyInfo"]):
                # 如果有属性的，就取第一条属性的值转为int型填写入对应的数组中的下标中
                key, index = i["Identifier"].split("_")
                tmp = key.split("current")[1]
                key = tmp[0:1].lower() + tmp[1:]
                result[key][int(index) - 1] = int(i["List"]["PropertyInfo"][0]["Value"])

        # 返回转化的结果
        return result


