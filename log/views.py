# _*_ coding:utf-8 _*_
import datetime

from log import models
from device import models as Dmodels
from utils.pagination import CommonPagination
from log.utils.serilizer import AlarmSerialiser, RunSerialiser

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class AlarmLogView(GenericViewSet):
    queryset = models.Alarm.objects.all()
    serializer_class = AlarmSerialiser
    pagination_class = CommonPagination

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        if request.user.fk_customer:
            uid = request.user.id
            device_name_list = Dmodels.Device.objects.filter(fk_user_id=uid).values_list('device_name', flat=True)
            param = {'device_name__in': device_name_list}
        else:
            param = {}

        alarm_list = models.Alarm.objects.order_by('-alarm_status', '-id').filter(**param)
        page = self.paginate_queryset(alarm_list)
        ser = self.get_serializer(instance=page, many=True)
        res['data'] = ser.data
        res['count'] = models.Alarm.objects.count()
        return Response(res)

    def limit(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        if request.user.fk_customer:
            uid = request.user.id
            device_name_list = Dmodels.Device.objects.filter(fk_user_id=uid).values_list('device_name', flat=True)
            param = {'device_name__in': device_name_list}
        else:
            device_name_list = []
            param = {}

        sign = kwargs.get('sign', None)
        if sign == 'startTime':
            start_time = request.data.get('data', None)
            if start_time is None:
                res['code'] = 1050
                res['msg'] = 'data参数缺失'
                return Response(res)

            # 暂时不设置大于小于
            # compare = request.data.get('compare', False)
            compare = True
            date_start_obj = datetime.datetime.fromtimestamp(start_time / 1000)
            if compare:
                param['alarm_starttime__gte'] = date_start_obj
                alarm_log_limit = models.Alarm.objects.filter(**param).order_by('-id')
            else:
                alarm_log_limit = models.Alarm.objects.filter(alarm_starttime__gte=date_start_obj).order_by('-id')
        elif sign == 'section':
            try:
                start_time, end_time = request.data.get('data', None)
            except Exception:
                res['code'] = 1050
                res['msg'] = 'data参数缺失'
                return Response(res)

            date_start_obj = datetime.datetime.fromtimestamp(start_time / 1000)
            date_end_obj = datetime.datetime.fromtimestamp(end_time / 1000)

            if date_start_obj > date_end_obj:
                res['code'] = 1051
                res['msg'] = '起始时间不能大于结束时间'
                return Response(res)

            param['alarm_starttime__gte'] = date_start_obj
            param['alarm_endtime__lte'] = date_end_obj
            alarm_log_limit = models.Alarm.objects.filter(**param).order_by('-id')
        elif sign == 'deviceName':
            device_name = request.data.get('data', None)
            if device_name is None:
                res['code'] = 1050
                res['msg'] = 'data参数缺失'
                return Response(res)

            if request.user.fk_customer and device_name not in device_name_list:
                res['code'] = 1051
                res['msg'] = '无此设备，请检查是否输入正确'
                return Response(res)

            alarm_log_limit = models.Alarm.objects.filter(device_name=device_name).order_by('-id')
        elif sign == 'status':
            status = request.data.get('data', None)
            if status is None:
                res['code'] = 1050
                res['msg'] = 'data参数缺失'
                return Response(res)

            param['alarm_status'] = status
            alarm_log_limit = models.Alarm.objects.filter(**param).order_by('-id')
        else:
            res['code'] = 1050
            res['msg'] = 'sign参数为无效值'
            return Response(res)

        page = self.paginate_queryset(alarm_log_limit)
        ser = self.get_serializer(instance=page, many=True)

        res['data'] = ser.data
        res['count'] = alarm_log_limit.count()
        return Response(res)


class RunLogView(GenericViewSet):
    queryset = models.Run.objects.all()
    serializer_class = RunSerialiser
    pagination_class = CommonPagination

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        if request.user.fk_customer:
            uid = request.user.id
            device_name_list = Dmodels.Device.objects.filter(fk_user_id=uid).values_list('device_name', flat=True)
            param = {'device_name__in': device_name_list}
        else:
            param = {}

        run_log_list = models.Run.objects.filter(**param).order_by('-id')

        pager = self.paginate_queryset(run_log_list)
        ser = self.get_serializer(instance=pager, many=True)

        res['data'] = ser.data
        res['count'] = models.Run.objects.count()
        return Response(res)

    def limit(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        if request.user.fk_customer:
            uid = request.user.id
            device_name_list = Dmodels.Device.objects.filter(fk_user_id=uid).values_list('device_name', flat=True)
            param = {'device_name__in': device_name_list}
        else:
            device_name_list = ''
            param = {}

        sign = kwargs.get('sign', None)
        if sign == 'startTime':
            start_time = request.data.get('data', None)
            if start_time is None:
                res['code'] = 1050
                res['msg'] = 'startTime参数缺失'
                return Response(res)

            # 暂时不设置大于小于
            # compare = request.data.get('compare', False)
            compare = True
            date_start_obj = datetime.datetime.fromtimestamp(start_time / 1000)
            if compare:
                param['run_starttime__gte'] = date_start_obj
                run_log_limit = models.Run.objects.filter(**param).order_by('-id')
            else:
                run_log_limit = models.Run.objects.filter(run_starttime__lte=date_start_obj).order_by('-id')
        elif sign == 'section':
            try:
                start_time, end_time = request.data.get('data', None)
            except Exception:
                res['code'] = 1050
                res['msg'] = 'startTime或endTime参数缺失'
                return Response(res)

            date_start_obj = datetime.datetime.fromtimestamp(start_time / 1000)
            date_end_obj = datetime.datetime.fromtimestamp(end_time / 1000)

            if date_start_obj > date_end_obj:
                res['code'] = 1051
                res['msg'] = '起始时间不能大于结束时间'
                return Response(res)

            param['run_endtime__lte'] = date_end_obj
            param['run_starttime__gte'] = date_start_obj
            run_log_limit = models.Run.objects.filter(**param).order_by('-id')
        elif sign == 'deviceName':
            device_name = request.data.get('data', None)
            if device_name is None:
                res['code'] = 1050
                res['msg'] = 'startTime或endTime参数缺失'
                return Response(res)

            if request.user.fk_customer and device_name not in device_name_list:
                res['code'] = 1051
                res['msg'] = '无此设备，请检查是否输入正确'
                return Response(res)

            run_log_limit = models.Run.objects.filter(device_name=device_name).order_by('-id')
        elif sign == 'count':
            res['count'] = models.Run.objects.filter(**param).count()
            return Response(res)
        else:
            res['code'] = 1050
            res['msg'] = 'sign参数为无效值'
            return Response(res)

        pager = self.paginate_queryset(run_log_limit)
        ser = self.get_serializer(instance=pager, many=True)

        res['data'] = ser.data
        res['count'] = run_log_limit.count()
        return Response(res)
