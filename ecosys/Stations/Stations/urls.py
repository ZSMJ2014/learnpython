"""Stations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from home.views import index, upload_data, submit_cols_num, show_chart, cal_bioindex

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^upload_data', upload_data),
    url(r'^submit_cols_num', submit_cols_num),
    url(r'^show_chart', show_chart),
    url(r'^cal_bioindex', cal_bioindex),
    url(r'^$', index),
]

