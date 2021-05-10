# _*_ coding:utf-8 _*_


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
