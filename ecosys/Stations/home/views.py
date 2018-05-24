# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import os

from django.http import HttpResponseBadRequest
from django import forms
from django.template import RequestContext
import django_excel as excel
# from django.utils import simplejson
import pandas as pd

# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, "index.html")


# def upload(request):
#     if request.method == "POST":
#         handle_upload_file(request.FILES['file'], str(request.FILES['file']))
#         return HttpResponse('Successful')  # 此处简单返回一个成功的消息，在实际应用中可以返回到指定的页面中
#
#     return render_to_response('course/upload.html')
#
#
# def handle_upload_file(file, filename):
#     path = 'media/uploads/'  # 上传文件的保存路径，可以自己指定任意的路径
#     if not os.path.exists(path):
#         os.makedirs(path)
#     with open(path + filename, 'wb+')as destination:
#         for chunk in file.chunks():
#             destination.write(chunk)


# Create your views here.
@csrf_exempt
def upload_data(request):
    f = request.FILES['datafile']
    excel_raw_data = pd.read_excel(f)
    cols=list(excel_raw_data.columns)
    # table=excel_raw_data.parse("菌类物种")
    # sheet = f.get_sheet()
    # array = f.get_array()

    # list = sheet.split('/n')
    # data = excel.make_response_from_array(list,'csv')
    # django-execl
    # data = excel.make_response(f.get_sheet(), "csv", file_name="sample")
    # file_content = data.getvalue().split(',')[10]


    # data_df = pd.read_csv(data)

    # with open('/tmp/%s' % f.name, 'w+') as w:
    #     for chunk in f.chunks():
    #         w.write(chunk)

    return HttpResponse(cols, content_type="application/json;charset=utf-8")
    # return HttpResponse(file_content)



