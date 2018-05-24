# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import os

from django.http import HttpResponseBadRequest
from django import forms
from django.template import RequestContext
# import django_excel as excel
# from django.utils import simplejson
import pandas as pd
import numpy as np
import math
import json

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
    pd.DataFrame.to_csv('/tmp/bio_data.csv')

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


def total_number_of_species(species):
    '''
    :param species: 物种类型列数据dataframe格式
    :return: 物种丰富度
    '''
    num = len(np.unique(species))
    return num

def species_distribution(species):
    '''
    :param species:物种类型列数据dataframe格式
    :return:物种数量分布，用于制作echarts
    '''
    unique = np.unique(species)
    spe_num = {}
    for s in unique:
        spe_num[s] = (species == s).sum()
    return spe_num

def simpson_index(species):
    '''
    :param species: 物种类型列数据dataframe格式
    :return: Simpson优势度指数
    '''
    spe_num = species_distribution(species)
    total_num = total_number_of_species(species)
    simpson_idx=1
    for s in spe_num.keys():
        p = float(spe_num[s]/total_num)
        simpson_idx = simpson_idx - p*p
    return simpson_idx

def shannonwiener_index(species):
    '''
    :param species: 物种类型列数据dataframe格式
    :return: Shannon-Wiener多样性指数
    '''
    spe_num = species_distribution(species)
    total_num = total_number_of_species(species)
    shannonwiener_idx = 0
    for s in spe_num.keys():
        p = float(spe_num[s] / total_num)
        shannonwiener_idx = shannonwiener_idx-p*math.log10(p)
    return shannonwiener_idx

def pielouaverage_index(species):
    '''
    :param species: 物种类型列数据dataframe格式
    :return: Pielou均匀度指数
    '''
    shannonwiener_idx = shannonwiener_index(species)
    total_num = total_number_of_species(species)
    pielouavg_idx = shannonwiener_idx/(math.log10(total_num))
    print("Pielou均匀度指数: %s"%pielouavg_idx)
    return pielouavg_idx

def cal_bioindex(request):
    df = pd.read_csv('/tmp/bio_data.csv')
#     parse the column from the request
    spec_col = 1
    species = df[[spec_col]]
    total_num_of_species = total_number_of_species(species)
    simpson_idx = simpson_index(species)
    shannonwiener_idx = shannonwiener_index(species)
    index_results = json.dumps({"物种丰富度": total_num_of_species, "Simpson优势度指数": simpson_idx, "Shannon-Wiener多样性指数": shannonwiener_idx })
    return HttpResponse(index_results, content_type="application/json; charset=utf-8")






