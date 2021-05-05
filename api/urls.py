# _*_ coding:utf-8 _*_

from django.urls import re_path

from api import views

urlpatterns = [
    re_path(r'^(?P<version>v\d+)/GetToken/$', views.UserView.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryDeviceList/$', views.QueryDeviceList.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryProductList/$', views.QueryProductList.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryPropertyList/$', views.QueryPropertyList.as_view()),
    re_path(r'^(?P<version>v\d+)/SetProperty/$', views.SetProperty.as_view()),
    re_path(r'^(?P<version>v\d+)/SetTask/$', views.SetTask.as_view()),


    # re_path(r'^(?P<version>v\d+)/device/$', views.DeviceView.as_view({'get': 'list'})),
    # re_path(r'^(?P<version>v\d+)/device/(?P<pk>\d+)/$', views.DeviceView.as_view({'get': 'list_limit', 'post': 'set'})),
    #
    # re_path(r'^(?P<version>v\d+)/property/$', views.PropertyView.as_view({'post': 'create'})),
]