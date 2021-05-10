# _*_ coding:utf-8 _*_

import json
import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api import models


class TaskSubmitView(GenericAPIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        res = {'code': 1000, 'msg': ''}

        device_name = request.data.get('deviceName', None)
        task_status = request.data.get('taskStatus', None)

        if device_name is None:
            res['code'] = 1050
            res['msg'] = 'deviceName参数缺失'
            return Response(res)

        task = models.Task.objects.filter(fk_device__device_name=device_name).first()

        url = task.taskSubmitUrl
        data = {
            'taskId': task.taskId,
            'taskStatus': task_status
        }
        task_info = json.loads(task.taskInfo)
        task_data = json.loads(task.taskSubmitInfo)
        for i in task_data:
            data[i] = task_info[i]

        # 统一提交任务格式为POST
        response = requests.post(url=url, data=data)
        if response.status_code != 200:
            res['code'] = 1053
            res['msg'] = f'提交任务失败，状态码：{response.status_code}'

        return Response(res)
