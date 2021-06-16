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


class WXLoginViewBK(APIView):
    """
    这个暂时不用了，直接使用PC端的账号和密码进行登录
    """
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        code = request.data.get('code', None)
        if code is None:
            res['code'] = 1050
            res['msg'] = '请求参数code不存在'
            return Response(res)

        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': 'wx1180797827e5a4d1',
            'secret': 'd2389770c8903ed26b66f559dfe8fd1c',
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        wx_user_info = requests.get(url=url, params=params).json()

        print("WXLoginView", wx_user_info)

        res['sessionKey'] = wx_user_info
        return Response(res)


class WXPhoneNumberView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        session_key = request.data.get('sessionKey', None)
        encrypted_data = request.data.get('encryptedData', None)
        iv = request.data.get('iv', None)
        if not session_key and encrypted_data and iv:
            res['code'] = 1051
            res['msg'] = '参数缺失'
            return Response(res)

        app_id = 'wx1180797827e5a4d1'

        pc = tool.WXBizDataCrypt(app_id, session_key)

        res['data'] = pc.decrypt(encrypted_data, iv)
        print(res['data'])
        return Response(res)


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
