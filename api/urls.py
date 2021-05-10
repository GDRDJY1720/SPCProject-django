# _*_ coding:utf-8 _*_

from django.urls import re_path

from api.views import user, task, device, product

urlpatterns = [
    re_path(r'^(?P<version>v\d+)/GetToken/$', user.GetTokenView.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryDeviceList/$', device.QueryDeviceListView.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryProductList/$', product.QueryProductListView.as_view()),
    re_path(r'^(?P<version>v\d+)/QueryPropertyList/$', task.QueryPropertyListView.as_view()),
    re_path(r'^(?P<version>v\d+)/SetProperty/$', task.SetPropertyView.as_view()),
    re_path(r'^(?P<version>v\d+)/SetTask/$', task.SetTaskView.as_view())
]