# _*_ coding:utf-8 _*_
import json
import time

from commonTool import ali_api
from device import models
from device.utils.permission import SVIPPermission
from device.utils.serializer import DeviceSerializer
from utils.pagination import CommonPagination
from product import models as Pmodels
from account import models as Umodels

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class DeviceInfoView(GenericViewSet):
    queryset = models.Device.objects.all()
    serializer_class = DeviceSerializer
    pagination_class = CommonPagination
    permission_classes = [SVIPPermission, ]

    Api = ali_api.AliDeviceAPI()

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        if request.user.from_privilege == 1:
            # 将数据对接放到管理员里面可以有效提高其他用户的访问速度
            # 但是如果是手动在物联网平台添加，没有管理员进行更新就不会产生新数据 （21-04-30）
            # ========================> 将物联网平台中的数据拷贝 <=====================
            product_list = Pmodels.Product.objects.exclude(product_type='test')
            # 与物联网平台中的数据对应
            for product in product_list:
                # 现在设备数量较少，当数据量多的时候需要多次调用接口来进行数据的对应
                dic = self.get_APIRun(res=res, APIname='QueryDevice', ProductKey=product.productkey, PageSize=50)
                if res['code'] != 1000:
                    return Response(res)

                tmp = dic.get('Data', None)
                if not tmp:
                    continue

                if len(tmp):
                    data_list = tmp.get('DeviceInfo')
                    for data in data_list:
                        models.Device.objects.update_or_create(device_name=data.get('DeviceName'),
                                                               defaults={
                                                                   'iot_id': data.get('IotId'),
                                                                   'from_product_id': product.id,
                                                                   # 'device_type': 1,
                                                                   'device_secret': data.get('DeviceSecret')
                                                               })
            # ========================> END <==============================================
            param = {}
        else:
            param = {'from_user_id': request.user.id}
        # 查询数据库中的数据传入到前端
        iot_list = models.Device.objects.exclude(from_product__product_type='test').filter(**param).order_by('-id').values_list(
            'iot_id', flat=True)
        if not iot_list:
            res['data'] = []
            res['count'] = 0
            return Response(res)

        pager = self.paginate_queryset(iot_list)
        state_dic = self.get_APIRun(res=res, APIname='BatchGetDeviceState', IotId_list=pager)
        if res['code'] != 1000:
            return Response(res)

        status_list = state_dic.get('DeviceStatusList').get('DeviceStatus')
        # 可以使用下面的方式将代码优化，但是不确定是不是只查询一次数据库
        # print(models.Device.objects.exclude(from_product__product_type='test').order_by('id'))
        de_list = models.Device.objects.filter(iot_id__in=pager).order_by('-id')
        ser = self.get_serializer(instance=de_list, many=True, context={'request': request, 'data': status_list})

        res['data'] = ser.data
        res['count'] = len(iot_list)
        return Response(res)

    def list_limit(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        if request.user.from_privilege == 1:
            param = {}
        else:
            param = {'from_user_id': request.user.id}

        sign = kwargs.get('pk', None)
        if sign == 'deviceName' or sign == 'id':
            data = request.query_params.get('data', None)
            if data is None:
                res['code'] = 1050
                res['msg'] = 'deviceName或id参数缺失'
                return Response(res)

            if sign == 'deviceName':
                sign = 'device_name'

            param[sign] = data
            device_list = models.Device.objects.filter(**param).order_by('-id')

        elif sign == 'productID':
            product_id = request.query_params.get('data', None)
            if product_id is None:
                res['code'] = 1050
                res['msg'] = 'productID参数缺失'
                return Response(res)

            param['from_product_id'] = product_id
            device_list = models.Device.objects.filter(**param).order_by('-id')

        elif sign == 'deviceSecret':
            device_secret = request.query_params.get('data', None)
            if device_secret is None:
                res['code'] = 1050
                res['msg'] = 'deviceSecret参数缺失'
                return Response(res)

            param['actual_device_secret'] = device_secret
            device_list = models.Device.objects.filter(**param).order_by('-id')

        elif sign == 'moduleSecret':
            module_secret = request.query_params.get('data', None)
            if module_secret is None:
                res['code'] = 1050
                res['msg'] = 'moduleSecret参数缺失'
                return Response(res)

            param['module_secret'] = module_secret
            device_list = models.Device.objects.filter(**param).order_by('-id')

        # 状态的筛选涉及到多次循环调用接口进行选择，同时也涉及到用户权限的问题，较为复杂，后续如有好方法再加
        # elif sign == 'status':
        #     status = request.query_params.get('data', None)
        #     if status is None:
        #         res['code'] = 1050
        #         res['msg'] = 'status参数缺失'
        #         return Response(res)
        #
        #     if request.user.from_privilege != 3:
        #         product_key_list = request.user.from_product.all().values_list('productkey', flat=True)
        #         for p in product_key_list:
        #             dic = self.get_APIRun(res=res, APIname='QueryDeviceByStatus',
        #                                   ProductKey=p, Status=status, CurrentPage=1, PageSize=10)
        #             if res['code'] != 1000:
        #                 return Response(res)
        #     print(request.user.from_product.all().values_list('productkey', flat=True))

        else:
            res['code'] = 1050
            res['msg'] = 'sign参数为无效值'
            return Response(res)

        if not len(device_list):
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        iot_id_list = device_list.values_list('iot_id', flat=True)
        pager = self.paginate_queryset(iot_id_list)
        state_dic = self.get_APIRun(res=res, APIname='BatchGetDeviceState', IotId_list=pager)
        if res['code'] != 1000:
            return Response(res)

        status_list = state_dic.get('DeviceStatusList').get('DeviceStatus')

        device_tmp_list = models.Device.objects.filter(iot_id__in=pager).order_by('-id')
        ser = self.get_serializer(instance=device_tmp_list, many=True,
                                  context={'request': request, 'data': status_list})
        res['data'] = ser.data
        res['count'] = device_list.count()
        return Response(res)

    def create(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}

        try:
            product_id = int(request.data.get('productID'))
        except Exception:
            res['code'] = 1010
            res['msg'] = 'str转int异常'
            return Response(res)

        nick_name = request.data.get('nickName', None)

        product = Pmodels.Product.objects.filter(id=product_id).first()
        device_name = 'GUTE_' + product.product_identifier + '_' + str(time.time()) + '_' + str(request.user.id)

        dic = self.get_APIRun(res=res, APIname='RegisterDevice', ProductKey=product.productkey,
                              Nickname=nick_name, DeviceName=device_name)
        if res['code'] != 1000:
            return Response(res)

        data = dic.get('Data')
        try:
            CDevice = models.Device.objects.create(nick_name=data.get('Nickname'),
                                                   device_name=data['DeviceName'],
                                                   device_secret=data['DeviceSecret'],
                                                   iot_id=data.get('IotId'),
                                                   from_product_id=product_id,
                                                   device_type=2)
        except Exception as e:
            res['code'] = 1011
            res['msg'] = 'create SQL异常 %s' % e
            return Response(res)

        # try:
        #     pro = request.user.from_product.filter(id=product_id, userinfo=request.user).first()
        #     if not pro:
        #         request.user.from_product.add(product)
        # except Exception as e:
        #     res['code'] = 1012
        #     res['msg'] = 'ManyToMany SQL异常 %s' % e
        #     return Response(res)

        ser = self.get_serializer(instance=CDevice, context={'request': request})
        res['data'] = ser.data

        return Response(res)

    def update(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        pk = kwargs.get('pk', None)

        device = models.Device.objects.filter(id=pk).first()
        if not device:
            res['code'] = 1014
            res['msg'] = 'device 不存在'
            return Response(res)

        old_user_id = device.from_user_id
        old_product_id = device.from_product_id
        nick_name = request.data.get('nickName', None)
        user_id = request.data.get('userId', None)
        device_secret = request.data.get('deviceSecret', None)
        module_secret = request.data.get('moduleSecret', None)

        if nick_name != device.nick_name and nick_name is not None:
            tmp = {
                'Nickname': nick_name,
                'IotId': device.iot_id
            }

            self.get_APIRun(res, 'BatchUpdateDeviceNickname', DeviceObjList=[tmp, ])
            if res['code'] != 1000:
                return Response(res)

        dic = {}
        if nick_name is not None:
            dic['nick_name'] = nick_name

        if user_id:
            dic['from_user_id'] = user_id

        if device_secret:
            dic['actual_device_secret'] = device_secret

        if module_secret:
            dic['module_secret'] = module_secret

        try:
            models.Device.objects.filter(id=pk).update(**dic)
        except Exception:
            res['code'] = 1011
            res['msg'] = '数据有重复'
            return Response(res)

        if user_id != device.from_user_id:
            i = models.Device.objects.filter(from_user_id=device.from_user_id,
                                             from_product_id=device.from_product_id).first()
            if not i:
                u = Umodels.UserInfo.objects.filter(id=old_user_id).first()
                if u:
                    u.from_product.remove(old_product_id)

        try:
            u = Umodels.UserInfo.objects.filter(id=user_id).first()
            u.from_product.add(old_product_id)
        except Exception as e:
            pass

        return Response(res)

    def destroy(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        pk = kwargs.get('pk', None)

        device = models.Device.objects.filter(id=pk).first()
        if not device:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        old_user_id = device.from_user_id
        old_product_id = device.from_product_id

        self.get_APIRun(res=res, APIname='DeleteDevice', IotId=device.iot_id)
        if res['code'] != 1000:
            return Response(res)

        device.delete()

        i = models.Device.objects.filter(from_user_id=old_user_id, from_product_id=old_product_id).first()
        if not i:
            u = Umodels.UserInfo.objects.filter(id=old_user_id).first()
            u.from_product.remove(old_product_id)

        return Response(res)

    def partial_update(self, request, *args, **kwargs):
        """
        效果与update基本相同，这个更自由
        """
        res = {'code': 1000, 'msg': ''}

        device_id = kwargs.get('pk', None)
        device = models.Device.objects.filter(id=device_id).first()

        old_user_id = device.from_user_id
        old_product_id = device.from_product_id

        sign = request.data.get('sign', None)
        if sign is None:
            res['code'] = 1050
            res['msg'] = '请求参数sign失缺'
            return Response(res)

        tmp = {}
        tmp[sign] = request.data.get('data', None)
        if tmp[sign] is None:
            res['code'] = 1050
            res['msg'] = '请求参数data缺失'
            return Response(res)

        if sign == 'nick_name':
            t = {
                'Nickname': tmp[sign],
                'IotId': device.iot_id
            }

            self.get_APIRun(res, 'BatchUpdateDeviceNickname', DeviceObjList=[t, ])
            if res['code'] != 1000:
                return Response(res)
        elif request.user.from_privilege == 3:
            res['code'] = 1006
            res['msg'] = '无更新权限'
            return Response(res)

        try:
            models.Device.objects.filter(id=device_id).update(**tmp)
        except Exception as e:
            print(e)
            res['code'] = 1011
            res['msg'] = '数据有重复'
            return Response(res)

        if sign == 'from_user_id':
            if tmp[sign] != device.from_user_id:
                i = models.Device.objects.filter(from_user_id=device.from_user_id,
                                                 from_product_id=device.from_product_id).first()
                if not i:
                    u = Umodels.UserInfo.objects.filter(id=old_user_id).first()
                    if u:
                        u.from_product.remove(old_product_id)

            try:
                u = Umodels.UserInfo.objects.filter(id=tmp[sign]).first()
                u.from_product.add(old_product_id)
            except Exception as e:
                pass

        return Response(res)

    def get_APIRun(self, res, APIname, **kwargs):
        try:
            dic = self.Api.APIRun(APIname, **kwargs)
        except Exception as e:
            res['code'] = 1003
            res['msg'] = '调用 APIRun：%s 出错' % APIname
            res['data'] = e
            return res

        if not dic.get('Success'):
            if not dic.get('ErrorMessage') == 'The specified device id is invalid.':
                res['code'] = 1004
                res['msg'] = '调用 APIRun：%s 失败' % APIname
                res['data'] = dic
                return res

        return dic


class DeviceDataView(GenericViewSet, ali_api.APIRun):
    queryset = models.Device.objects.all()
    serializer_class = DeviceSerializer
    pagination_class = CommonPagination

    Api = ali_api.AliDeviceAPI()

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        product_id = request.query_params.get('productID', None)
        if product_id is None:
            res['code'] = 1050
            res['msg'] = 'productID参数缺失'
            return Response(res)

        if request.user.from_privilege == 1:
            param = {'from_product_id': product_id}
        else:
            param = {'from_user_id': request.user.id, 'from_product_id': product_id}

        device_list = models.Device.objects.filter(**param).order_by('-id')
        iot_id_list = device_list.values_list('iot_id', flat=True)
        dic = self.get_api_run(res=res, api_name='BatchGetDeviceState', IotId_list=iot_id_list)
        if res['code'] != 1000:
            return Response(res)

        device_status = dic.get('DeviceStatusList').get('DeviceStatus')
        device_name = list()
        for de in device_status:
            if de.get('Status') == "ONLINE":
                device_name.append(de.get('DeviceName'))

        device_online_list = models.Device.objects.filter(device_name__in=device_name)
        ser = self.get_serializer(instance=device_online_list, many=True)
        res['data'] = ser.data
        return Response(res)


class DeviceLockView(GenericViewSet, ali_api.APIRun):
    queryset = models.Device.objects.all()
    serializer_class = None
    pagination_class = CommonPagination

    Api = ali_api.AliPropertyAPI()

    def lock(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        params = {}

        sign = request.data.get('sign', 'deviceId')
        data = request.data.get('data', None)
        if data is None:
            res['code'] = 1050
            res['msg'] = 'sign的具体参数缺失'
            return Response(res)

        if sign == 'deviceId':
            params['id'] = data
        elif sign == 'deviceName':
            params['device_name'] = data

        device_obj = models.Device.objects.filter(**params).first()
        if not device_obj:
            res['code'] = 1010
            res['msg'] = '设备不存在'
            return Response(res)

        lockFlag = int(request.data.get('lockFlag', '1'))
        # lockFlag == 1表示为立即锁定，0为解除锁定
        if lockFlag:
            items = '{"DeviceOnLock":1}'

            self.get_api_run(res=res, api_name='SetDeviceProperty', Items=items,
                             IotId=device_obj.iot_id)
            if res['code'] != 1000:
                return Response(res)

            models.Device.objects.filter(**params).update(deviceOnLock=True)

        else:
            items = '{"DeviceOnLock":0}'

            self.get_api_run(res=res, api_name='SetDeviceProperty', Items=items,
                             IotId=device_obj.iot_id)
            if res['code'] != 1000:
                return Response(res)

            models.Device.objects.filter(**params).update(deviceOnLock=False)

        return Response(res)

