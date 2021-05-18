# _*_ coding:utf-8 _*_
from rest_framework.views import exception_handler as drf_exception_handler

from rest_framework.views import Response

from rest_framework import status


def exception_handler(exc, context):
    # drf的exception_handler做基础处理

    response = drf_exception_handler(exc, context)
    print(response)

    # 为空，说明 drf 中没有对应的处理，咱们自定义二次处理

    if response is None:
        # print(exc)

        # # Book matching query does not exist

        # print(context)

        # # {'view': <api.views.Book object at 0x000001FED29DD860>}, 'args': (), 'kwargs': {'pk': '4'}, 'request': <rest_framework.request.Request object at 0x000001FED2CD9EF0>

        # 这里后期应该写成系统日志才对（这只是演示的伪代码）

        print('%s - %s - %s' % (context['view'], context['request'].method, exc))

        # <api.views.Book object at 0x000002505A2A9A90> - GET - Book matching query does not exits.

        return Response({

            'detail': '服务器错误'

        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=True)

    return response
