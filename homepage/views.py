# _*_ coding:utf-8 _*_

import datetime
import time

from homepage.utils.permission import SVIPPermission
from homepage.utils import serializer
from commonTool import ali_api, tool
from utils.pagination import CommonPagination
from device import models as Dmodels
from product import models as Pmodels
from account import models as Umodels
from log import models as Lmodels

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, ViewSet


class HomepageInfo(GenericAPIView, ali_api.APIRun):
    pagination_class = CommonPagination
    Api = ali_api.AliDeviceAPI()

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        if request.user.fk_customer:
            param = {'fk_user_id': request.user.id}
        else:
            param = {}

        device_list = Dmodels.Device.objects.filter(**param).order_by('-id')
        data = dict()
        data.update({
            "count": 0,
            "device": {
                "online": 0,
                "offline": 0,
                "unactive": 0,
                "disable": 0
            },
            "table": [],
            "log": {
                "alarm": {},
                "run": {}
            }
        })

        # 将状态重新加上
        device_iot = device_list.values_list('iot_id', flat=True)
        if not device_iot:
            res['code'] = 1005
            res['msg'] = '暂无设备，请联系管理员'
            return Response(res)
        device_iot_pager = self.paginate_queryset(device_iot)

        dic = self.get_api_run(res=res, api_name='BatchGetDeviceState', IotId_list=device_iot_pager)
        if res['code'] != 1000:
            return Response(res)

        device_status = dic.get('DeviceStatusList').get('DeviceStatus')
        # 组合设备信息表格，用于生成首页表格
        device_table = device_list.values('device_name',
                                          'nick_name',
                                          'device_TotalRunTime',
                                          'device_TotalOutput')
        device_table_pager = self.paginate_queryset(device_table)

        # 生成设备状态数据信息，将管理员和其他用户分开，管理员直接调用API，其他人员使用对比获取
        if request.user.fk_customer is None:
            dic = self.get_api_run(res=res, api_name='QueryDeviceStatistics')
            if res['code'] != 1000:
                return Response(res)

            data['count'] = dic.get('Data').get('deviceCount')
            online = dic.get('Data').get('onlineCount')
            active = dic.get('Data').get('activeCount')
            data["device"]["unactive"] = data['count'] - active
            data["device"]["offline"] = active - online
            data["device"]["online"] = online
            data["device"]["disable"] = active - data["device"]["offline"] - data["device"]["online"]

            for de in device_status:
                for tab in device_table_pager:
                    if tab['device_name'] == de.get('DeviceName'):
                        tab['status'] = tool.data_status_transform(de.get('Status'))
                        break

        else:
            data["count"] = device_list.count()
            for de in device_status:
                for tab in device_table_pager:
                    if tab['device_name'] == de.get('DeviceName'):
                        tab['status'] = tool.data_status_transform(de.get('Status'))
                        break
                if de.get('Status') == "UNACTIVE":
                    data["device"]["unactive"] += 1
                elif de.get('Status') == "OFFLINE":
                    data["device"]["offline"] += 1
                elif de.get('Status') == "ONLINE":
                    data["device"]["online"] += 1
                else:
                    data["device"]["disable"] += 1

        data['table'] = device_table_pager

        device_name = device_list.values_list('device_name', flat=True)
        # 2、从运行日志中获取到昨日的总运行时间和总运行设备数量（日志功能未完成，现数据为模拟数据 3-14）
        today = datetime.datetime.fromtimestamp(time.mktime(datetime.date.today().timetuple()))
        yesterday = today - datetime.timedelta(days=1)
        # 管理员的时候就是全部搜索，不需要使用deviceName进行限制
        if request.user.fk_customer:
            log_params = {'device_name__in': device_name}
        else:
            log_params = {}

        run_log_list = Lmodels.Run.objects.filter(run_starttime__gte=yesterday,
                                                  run_endtime__lte=today,
                                                  **log_params)
        run_log_device = run_log_list.values('device_name', 'run_starttime')
        data["log"]["run"] = self.get_run_log_data(yesterday, run_log_device)

        # 3、将报警日志做成折线图，x轴为时间，以天为单位，y轴为次数
        alarm_log_list = Lmodels.Alarm.objects.filter(**log_params).values_list('alarm_starttime', flat=True)
        data["log"]["alarm"] = self.get_alarm_log_data(alarm_log_list)

        res['data'] = data
        return Response(res)

    @staticmethod
    def get_run_log_data(yesterday, data):
        date_dic = {}
        date_list = []
        for i in range(0, 24):
            tmp = (yesterday + datetime.timedelta(hours=i)).strftime('%H:%M')
            date_dic[tmp] = 0
            date_list.append(tmp)
        for d in data:
            date = d['run_starttime'] - yesterday
            hour = round(date.seconds / 3600)
            if date.days > 1:
                continue
            else:
                date_dic[date_list[hour]] += 1

        return date_dic

    @staticmethod
    def get_alarm_log_data(data):
        tmp = {}
        for d in data:
            try:
                tmp[d.strftime("%Y-%m-%d")] += 1
            except Exception:
                tmp[d.strftime("%Y-%m-%d")] = 1

        return tmp

class HomepageInfoTable(GenericAPIView, ali_api.APIRun):
    """
    专门用于获取懒加载表格的数据
    """
    pagination_class = CommonPagination
    Api = ali_api.AliDeviceAPI()

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        if request.user.fk_customer:
            param = {'fk_user_id': request.user.id}
        else:
            param = {}

        device_list = Dmodels.Device.objects.filter(**param).order_by('-id')

        device_iot = device_list.values_list('iot_id', flat=True)
        if not device_iot:
            res['code'] = 1005
            res['msg'] = '暂无设备，请联系管理员'
            return Response(res)
        device_iot_pager = self.paginate_queryset(device_iot)

        dic = self.get_api_run(res=res, api_name='BatchGetDeviceState', IotId_list=device_iot_pager)
        if res['code'] != 1000:
            return Response(res)

        device_status = dic.get('DeviceStatusList').get('DeviceStatus')
        # 组合设备信息表格，用于生成首页表格
        device_table = device_list.values('device_name',
                                          'nick_name',
                                          'device_TotalRunTime',
                                          'device_TotalOutput')
        device_table_pager = self.paginate_queryset(device_table)

        for de in device_status:
            for tab in device_table_pager:
                if tab['device_name'] == de.get('DeviceName'):
                    tab['status'] = tool.data_status_transform(de.get('Status'))
                    break

        res['data'] = device_table_pager

        return Response(res)


class HomepageMap(APIView, ali_api.APIRun):
    Api = ali_api.AliDeviceAPI()

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        if request.user.fk_customer:
            param = {'fk_user_id': request.user.id, 'device_type': 2}
        else:
            param = {'device_type': 2}

        device_list = Dmodels.Device.objects.filter(**param)
        for device in device_list:
            tmp = {
                "id": device.id,
                "lng": device.device_longitude,
                "lat": device.device_latitude
            }
            res['data'].append(tmp)

        return Response(res)


class HomepageDataV(GenericAPIView, ali_api.APIRun):
    """
    此接口只允许管理员调用
    """
    pagination_class = CommonPagination
    permission_classes = [SVIPPermission, ]
    Api = ali_api.AliDeviceAPI()

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        data = dict()
        data.update({
            "count": 0,
            "device": {}
        })

        # 1、设备总量及状态统计
        dic = self.get_api_run(res=res, api_name='QueryDeviceStatistics')
        if res['code'] != 1000:
            return Response(res)

        data['count'] = dic.get('Data').get('deviceCount')
        online = dic.get('Data').get('onlineCount')
        active = dic.get('Data').get('activeCount')
        data["device"]["unActive"] = data['count'] - active
        data["device"]["offline"] = active - online
        data["device"]["online"] = online
        # data["device"]["disable"] = active - data["device"]["offline"] - data["device"]["online"]

        # 2、各产品设备数量统计
        product_list = Pmodels.Product.objects.exclude(product_type='test')
        product_ser = serializer.ProductCountSerializer(instance=product_list, many=True)
        data['product'] = product_ser.data

        # 3、地图销量展示
        map_list = Dmodels.Device.objects.filter(device_type=2).exclude(actual_device_secret=None).values(
            'device_province').annotate(count=Dmodels.models.Count('device_province'))
        # device_ser = serializer.DeviceMapSerializer(instance=device_list, many=True)
        data['map'] = map_list

        # 4、本周设备运行情况
        today = datetime.datetime.today()
        last_week = today - datetime.timedelta(days=7)
        run_log_list = Lmodels.Run.objects.filter(run_starttime__gte=last_week, run_endtime__lte=today).values(
            'run_starttime')
        run_data = self.get_run_log_data(last_week, run_log_list)
        data['run'] = run_data

        # # 5、运行信息
        # device_table = Dmodels.Device.objects.values('device_name',
        #                                              'device_TotalRunTime',
        #                                              'device_TotalOutput').order_by('-id')
        # pager_run = self.paginate_queryset(device_table)
        # data['runLog'] = pager_run
        #
        # # 6、报警信息
        # alarm_list = Lmodels.Alarm.objects.all().order_by('-id')
        # pager_alarm = self.paginate_queryset(alarm_list)
        # alarm_ser = serializer.AlarmLogSerializer(instance=pager_alarm, many=True)
        # data['alarmLog'] = alarm_ser.data
        # data['alarmLogCount'] = alarm_list.count()

        res['data'] = data
        return Response(res)

    @staticmethod
    def get_run_log_data(last_time, data):
        date_dic = {}
        date_list = []
        for i in range(0, 7):
            tmp = (last_time + datetime.timedelta(days=i)).strftime('%m-%d')
            date_dic[tmp] = 0
            date_list.append(tmp)
        for d in data:
            date = d['run_starttime'] - last_time
            day = round(date.seconds / (3600 * 24))
            date_dic[date_list[day]] += 1

        return date_dic


class HomepageDataVAlarm(GenericAPIView):
    permission_classes = [SVIPPermission, ]
    pagination_class = CommonPagination

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        alarm_list = Lmodels.Alarm.objects.all().order_by('-id')
        pager_alarm = self.paginate_queryset(alarm_list)
        alarm_ser = serializer.AlarmLogSerializer(instance=pager_alarm, many=True)
        res['data'] = alarm_ser.data
        res['count'] = alarm_list.count()
        return Response(res)


class HomepageDataVRun(GenericAPIView):
    permission_classes = [SVIPPermission, ]
    pagination_class = CommonPagination

    def get(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        device_table = Dmodels.Device.objects.values('device_name',
                                                     'device_TotalRunTime',
                                                     'device_TotalOutput').order_by('-id')
        pager_run = self.paginate_queryset(device_table)
        res['data'] = pager_run
        res['count'] = device_table.count()
        return Response(res)
