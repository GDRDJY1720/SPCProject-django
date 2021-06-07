# _*_ coding:utf-8 _*_

import time

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.db.utils import IntegrityError

from utils.pagination import CommonPagination
from account.tool import account
from account import models
from account.utils import auth, serializer


class UserView(GenericViewSet):
    authentication_classes = [auth.UserCreateAuth]
    queryset = models.UserInfo.objects.all()
    serializer_class = serializer.UserSerialiser
    pagination_class = CommonPagination

    def list(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        user_list = models.UserInfo.objects.all()
        ser = self.get_serializer(instance=user_list, many=True)
        res['data'] = ser.data
        return Response(res)

    def info(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        pk = kwargs.get('pk', None)
        user = models.UserInfo.objects.filter(id=pk).first()
        ser = self.get_serializer(instance=user)
        res['data'] = ser.data
        return Response(res)

    @staticmethod
    def create(request, *args, **kwargs):
        """
        数据库无法置唯一，只有创建的时候进行控制了
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        res = {'code': 1000, 'msg': ''}

        stime = str(time.time())
        username = request.data.get('userName', None)
        phone_num = request.data.get('phoneNum', None)
        password = account.md5(username, [request.data.get('password', None), phone_num])
        user_id = account.md5('api' + username, stime)
        user_secret = account.md5(user_id, [password, stime])

        data = {
            'username': username,
            'password': password,
            'user_email': request.data.get('userEmail', None),
            'phone_num': phone_num,
            'privilege': request.data.get('privilege', None),
            'user_id': user_id,
            'user_secret': user_secret,
        }

        try:
            models.UserInfo.objects.create(**data)
        except IntegrityError as i:
            print(i)
            res['code'] = 1018
            res['msg'] = ''
            return Response(res)
        except Exception as e:
            print(e)
            res['code'] = 1011
            res['msg'] = 'create SQL错误'
            return Response(res)
        return Response(res)

    @staticmethod
    def destroy(request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        pk = kwargs.get('pk', None)
        if pk == '1':
            res['code'] = 1017
            res['msg'] = '不能删除管理员'
            return Response(res)
        models.UserInfo.objects.filter(id=pk).delete()
        return Response(res)

    @staticmethod
    def update(request, *args, **kwargs):
        res = {'code': 1000, 'msg': '', 'data': []}
        return Response(res)
