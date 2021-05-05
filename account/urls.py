# _*_ coding:utf-8 _*_

from django.urls import re_path
from account.views import account, user

urlpatterns = [
    re_path(r'^login/$', account.LoginView.as_view()),
    # re_path(r'^logout/(?P<did>[0-9]+)/$', account.LogoutView.as_view()),

    re_path(r'^user/$', user.UserView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^user/(?P<pk>\d+)/$', user.UserView.as_view({'get': 'info', 'put': 'update', 'delete': 'destroy'})),
]

