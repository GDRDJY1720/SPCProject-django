# _*_ coding:utf-8 _*_

from django.urls import re_path
from weixin.views import account, device, property, sale

urlpatterns = [
    re_path(r'^login/$', account.WXLoginView.as_view()),

    # re_path(r'^phone/$', account.WXPhoneNumberView.as_view()),

    re_path(r'^device/$', device.WXDeviceInfoView.as_view({'post': 'post'})),
    re_path(r'^device/(?P<pk>\w+)/$', device.WXDeviceInfoView.as_view({'put': 'update'})),

    re_path(r'^property/$', property.WXPropertyView.as_view()),
    re_path(r'^setProperties/$', property.WXSetProperties.as_view()),

    re_path(r'^sale/$', sale.WXSaleView.as_view({'post': 'create'})),
    re_path(r'^sale/(?P<sign>\w+)/$', sale.WXSaleView.as_view({'put': 'update_info'})),
]
