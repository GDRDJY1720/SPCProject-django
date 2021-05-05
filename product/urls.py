# _*_ coding:utf-8 _*_

from django.urls import re_path
from product.views import product

urlpatterns = [
    re_path(r'^info/$', product.ProductView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^info/(?P<pk>\d+)/$',
            product.ProductView.as_view(
                {'get': 'list_limit', 'delete': 'destroy', 'put': 'update', 'patch': 'partial_update'})),
]