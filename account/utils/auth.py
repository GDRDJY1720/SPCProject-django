# _*_ coding:utf-8 _*_

import json

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from account import models


class UserCreateAuth(BaseAuthentication):
    def authenticate(self, request):
        if request.method == "POST":
            return

        res = {'code': 1000, 'msg': ''}

        token = request.query_params.get('token') or request.POST.get('token') or request.data.get('token')
        token_obj = models.UserToken.objects.filter(token=token).first()
        if not token_obj:
            # raise exceptions.AuthenticationFailed(detail='用户验证失败', code=1001)
            res['code'] = 1001
            res['msg'] = '用户验证失败'
            raise exceptions.AuthenticationFailed(res)

        return token_obj.fk_user, token_obj
