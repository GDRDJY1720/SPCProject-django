# _*_ coding:utf-8 _*_

import time
import datetime

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from account import models


class Authtiction(BaseAuthentication):
    def authenticate(self, request):
        res = {'code': 1000, 'msg': ''}
        token = request.query_params.get('token') or request.POST.get('token') or request.data.get('token')
        token_obj = models.UserToken.objects.filter(token=token).first()
        if not token_obj:
            res['code'] = 1001
            res['msg'] = '登录失败，请重新登录'
            raise exceptions.AuthenticationFailed(res)

        # 需要添加事件验证，当起始时间大于一天的时候，返回到登录页面重新登录 21-2-4
        if datetime.datetime.now() > token_obj.end_time:
            res['code'] = 1001
            res['msg'] = '登录超时，请重新登录'
            raise exceptions.AuthenticationFailed(res)

        return token_obj.fk_user, token_obj
