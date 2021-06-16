# _*_ coding:utf-8 _*_

import time
import datetime

from account.utils import serializer
from account.tool import account
from account import models

import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from weixin.utils import tool


class WXLoginView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': None}
        ser = serializer.LoginSerializer(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['username']

            if user.password != account.md5(user.username, [ser.validated_data['password'], user.phone_num]):
                res['msg'] = '密码错误'
                res['code'] = 1002
                return Response(res)

            stime = time.time()
            now = datetime.datetime.now()
            token_obj = models.UserToken.objects.filter(fk_user_id=user.id).first()
            if token_obj is None or now > token_obj.end_time:
                time_out = now + datetime.timedelta(days=1)
                m = account.md5(user.phone_num, stime)
                token_obj, flag = models.UserToken.objects.update_or_create(fk_user=user,
                                                                            defaults={'start_time': now,
                                                                                      'token': m,
                                                                                      'end_time': time_out})
            token_ser = serializer.TokenSerializer(instance=token_obj, context={'request': request})
            res['data'] = token_ser.data
            return Response(res)
        else:
            msg = ser.errors.get('username', None) or ser.errors.get('password', None)
            res['code'] = 1001
            res['msg'] = msg[0]
            return Response(res)
