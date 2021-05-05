# _*_ coding:utf-8 _*_

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from account import models

class APIAuthtiction(BaseAuthentication):
    def authenticate(self, request):
        res = {'code': 1000, 'msg': ''}
        user_id = request.query_params.get('user_id') or request.POST.get('user_id') or request.data.get('user_id')
        user_secret = request.query_params.get('user_secret') or request.POST.get('user_secret') or request.data.get(
            'user_secret')

        user = models.UserInfo.objects.filter(user_id=user_id, user_secret=user_secret).first()
        if not user:
            res['code'] = 1001
            res['msg'] = '用户标识验证错误'
            raise exceptions.AuthenticationFailed(res)

