# _*_ coding:utf-8 _*_

import time
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from api.utils import serializers
from account import models as Umodels
from account.tool import account


class GetTokenView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}
        tmp = serializers.UserSerializer(data=request.data, context={'user': None})
        if tmp.is_valid():
            # 创建token
            user = tmp.context['user']
            stime = time.time()
            now = datetime.datetime.now()
            token_obj = Umodels.UserToken.objects.filter(user_id=user.id).first()
            if token_obj is None or now > token_obj.end_time:
                time_out = now + datetime.timedelta(days=1)
                m = account.md5(user.phone_num, stime)
                Umodels.UserToken.objects.update_or_create(user=user,
                                                           defaults={'start_time': now,
                                                                     'token': m,
                                                                     'end_time': time_out})
            else:
                m = token_obj.token
            # 返回
            res['token'] = m
            return Response(res)
        else:
            res['code'] = tmp.errors.get('non_field_errors')[0].code
            res['msg'] = tmp.errors.get('non_field_errors')[0]
            return Response(res)



