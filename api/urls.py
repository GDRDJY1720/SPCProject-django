# _*_ coding:utf-8 _*_

from django.urls import re_path

from api.views import user, task, device, submit

urlpatterns = [
    # 用于用户登录
    re_path(r'^(?P<version>v\d+)/GetToken/$', user.GetTokenView.as_view()),

    # 查询设备列表
    re_path(r'^(?P<version>v\d+)/QueryDeviceList/$', device.QueryDeviceListView.as_view()),

    # 查询属性列表
    re_path(r'^(?P<version>[v1]+)/QueryPropertyList/$', task.QueryPropertyListView.as_view()),
    re_path(r'^(?P<version>[v2]+)/QueryPropertyList/$', task.V2QueryPropertyListView.as_view()),

    # 任务下载
    re_path(r'^(?P<version>[v1]+)/SetTask/$', task.SetTaskView.as_view()),
    re_path(r'^(?P<version>[v2]+)/SetTask/$', task.V2SetTaskView.as_view()),
    # 查询当前任务
    re_path(r'^(?P<version>[v2]+)/QueryDeviceTask/$', task.V2QueryDeviceTaskView.as_view()),
    # 任务完成提交
    re_path(r'^(?P<version>v\d+)/TaskSubmit/$', submit.TaskSubmitView.as_view()),

    # 设备操控接口
    # 启动
    re_path(r'^(?P<version>[v2]+)/StartDevice/$', device.StartDeviceView.as_view()),
    # 停止
    re_path(r'^(?P<version>[v2]+)/StopDevice/$', device.StopDeviceView.as_view()),
    # 暂停
    re_path(r'^(?P<version>[v2]+)/PauseDevice/$', device.PauseDeviceView.as_view()),
]