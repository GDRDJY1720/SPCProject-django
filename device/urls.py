# _*_ coding:utf-8 _*_

from django.urls import re_path
from device.views import device, property

urlpatterns = [
    re_path(r'^info/$', device.DeviceInfoView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^info/(?P<pk>\w+)/$', device.DeviceInfoView.as_view(
        {'get': 'list_limit', 'delete': 'destroy', 'put': 'update', 'patch': 'partial_update'})),

    re_path(r'^data/$', device.DeviceDataView.as_view({'get': 'list'})),

    re_path(r'^lock/$', device.DeviceLockView.as_view({'post': 'lock'})),

    # re_path(r'^property/$', property.PropertyInfoView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^property/(?P<pk>\w+)/$', property.PropertyInfoView.as_view({'get': 'list', 'post': 'data'})),
    re_path(r'^setProperty/$', property.SetPropertyView.as_view({'get': 'list', 'post': 'set'}))


]
