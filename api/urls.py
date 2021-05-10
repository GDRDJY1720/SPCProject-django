# _*_ coding:utf-8 _*_

from django.urls import re_path

from api.views import api, task

urlpatterns = [
    re_path(r'^(?P<version>v\d+)/GetToken/$', api.UserView.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryDeviceList/$', api.QueryDeviceList.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryProductList/$', api.QueryProductList.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryPropertyList/$', api.QueryPropertyList.as_view()),
    re_path(r'^(?P<version>v\d+)/SetProperty/$', api.SetProperty.as_view()),
    re_path(r'^(?P<version>v\d+)/SetTask/$', api.SetTask.as_view()),


    # re_path(r'^(?P<version>v\d+)/device/$', views.DeviceView.as_view({'get': 'list'})),
    # re_path(r'^(?P<version>v\d+)/device/(?P<pk>\d+)/$', views.DeviceView.as_view({'get': 'list_limit', 'post': 'set'})),
    #
    # re_path(r'^(?P<version>v\d+)/property/$', views.PropertyView.as_view({'post': 'create'})),
]