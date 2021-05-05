# _*_ coding:utf-8 _*_
import time
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from account.utils import serializer
from account.tool import account
from account import models


class LoginView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': None}
        ser = serializer.LoginSerialiser(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['phoneNum']

            if user.password != account.md5(user.username, [ser.validated_data['password'], user.phonenum]):
                res['msg'] = '密码错误'
                res['code'] = 1002
                return Response(res)

            stime = time.time()
            now = datetime.datetime.now()
            token_obj = models.UserToken.objects.filter(user_id=user.id).first()
            if token_obj is None or now > token_obj.end_time:
                time_out = now + datetime.timedelta(days=1)
                m = account.md5(user.phonenum, stime)
                token_obj, flag = models.UserToken.objects.update_or_create(user=user,
                                                                            defaults={'start_time': now,
                                                                                      'token': m,
                                                                                      'end_time': time_out})
            token_ser = serializer.TokenSerialiser(instance=token_obj, context={'request': request})
            res['data'] = token_ser.data
            return Response(res)
        else:
            msg = ser.errors.get('phonenum', None) or ser.errors.get('password', None)
            res['code'] = 1001
            res['msg'] = msg[0]
            return Response(res)


# 登出接口无用， 用户登出一般来说不会使用登出函数，前端处理掉登录信息即可
# 后端如果要做这个接口也是可以的，但是是使用POST请求即可
# class LogoutView(APIView):
#     def delete(self, request, *args, **kwargs):
#         res = {'code': 1000, 'msg': None}
#         obj = models.UserToken.objects.filter(user_id=kwargs['did']).delete()
#         return Response(res)
