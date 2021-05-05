# _*_ coding:utf-8 _*_

from django.urls import re_path
from homepage import views

urlpatterns = [
    re_path(r'^info/$', views.HomepageInfo.as_view()),
    re_path(r'^info/table/$', views.HomepageInfoTable.as_view()),
    re_path(r'^map/$', views.HomepageMap.as_view()),
    re_path(r'^dataV/$', views.HomepageDataV.as_view()),
    re_path(r'^dataV/alarm/$', views.HomepageDataVAlarm.as_view()),
    re_path(r'^dataV/run/$', views.HomepageDataVRun.as_view())
]