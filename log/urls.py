# _*_ coding:utf-8 _*_

from django.urls import re_path
from log import views

urlpatterns = [
    re_path(r'^alarm/$', views.AlarmLogView.as_view({'get': 'list'})),
    re_path(r'^alarm/(?P<sign>\w+)/$', views.AlarmLogView.as_view({'post': 'limit'})),

    re_path(r'^run/$', views.RunLogView.as_view({'get': 'list'})),
    re_path(r'^run/(?P<sign>\w+)/$', views.RunLogView.as_view({'post': 'limit'}))
]
