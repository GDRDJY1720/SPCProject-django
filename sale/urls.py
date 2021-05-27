# _*_ coding:utf-8 _*_


from django.urls import re_path
from sale.views import sales

urlpatterns = [
    re_path(r'^info/$', sales.SalesInfo.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy',
                                                 'put': 'update'})),
    re_path(r'^info/(?P<sign>\w+)/$', sales.SalesInfo.as_view({'get': 'list_limit', 'put': 'update_info'}))
]