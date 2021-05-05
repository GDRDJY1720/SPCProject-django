"""project_21_01_25 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path

urlpatterns = [
    path('spc/account/', include('account.urls')),
    path('spc/homepage/', include('homepage.urls')),
    path('spc/device/', include('device.urls')),
    path('spc/product/', include('product.urls')),
    path('spc/log/', include('log.urls')),
    # path('file/', include('Data.urls')),

    path('spc/wx/', include('weixin.urls')),
    path('api/', include('api.urls')),
]
