# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response

# Create your views here.
from django.http.response import HttpResponse
from django.core import serializers
from statistics import models
import json
import os

#查询页面请求的运营商统计数据
def get_operator_data(reuqest):

    traffic_time = models.Operator_compute_result.objects.all().order_by('-id')[0:1]
    traffic_time_s = serializers.serialize("json", traffic_time)
    traffic_time_json = json.loads(traffic_time_s)
    print traffic_time_json[0]["fields"]
    print type(traffic_time_json[0]["fields"])
    start_time_data = traffic_time_json[0]["fields"]["start_time"]
    end_time_data = traffic_time_json[0]["fields"]["end_time"]
    max_value_data = traffic_time_json[0]["fields"]["max_value"]
    average_value_data = traffic_time_json[0]["fields"]["average_value"]
    data_dit = {"start_time":start_time_data,"end_time":end_time_data,"max_value":max_value_data,"average_value":average_value_data}

    return HttpResponse(json.dumps(data_dit))

#查询接口请求的运营商统计数据
def get_operator_api_data(request):

    month_data_list = []
    BGP_max_data_list = []
    BGP_average_data_list = []
    LT_max_data_list = []
    LT_average_data_list = []
    DX_max_data_list = []
    DX_average_data_list = []
    YD_YZ_max_data_list = []
    YD_YZ_average_data_list = []
    YD_YF_max_data_list = []
    YD_YF_average_data_list = []
    all_data = models.Operator_month_count.objects.all().order_by('create_time')
    all_data_s = serializers.serialize("json",all_data)
    all_data_json = json.loads(all_data_s)
    for item in all_data_json:
        item_operator_data = item['fields']['operator']
        item_area_data = item['fields']['comment']
        item_month_data = item['fields']['month']
        month_data_list.append(item_month_data)
        if item_operator_data == 'BGP':
            item_BGP_max_data = item['fields']['max_value']
            item_BGP_average_data = item['fields']['average_value']
            BGP_max_data_list.append(item_BGP_max_data)
            BGP_average_data_list.append(item_BGP_average_data)
        elif item_operator_data == 'LT':
            item_LT_max_data = item['fields']['max_value']
            item_LT_average_data = item['fields']['average_value']
            LT_max_data_list.append(item_LT_max_data)
            LT_average_data_list.append(item_LT_average_data)
        elif item_operator_data == 'DX':
            item_DX_max_data = item['fields']['max_value']
            item_DX_average_data = item['fields']['average_value']
            DX_max_data_list.append(item_DX_max_data)
            DX_average_data_list.append(item_DX_average_data)
        elif item_operator_data == 'YD' and item_area_data == 'YZ':
            item_YD_YZ_max_data = item['fields']['max_value']
            item_YD_YZ_average_data = item['fields']['average_value']
            YD_YZ_max_data_list.append(item_YD_YZ_max_data)
            YD_YZ_average_data_list.append(item_YD_YZ_average_data)
        elif item_operator_data == 'YD' and item_area_data == 'YF':
            item_YD_YF_max_data = item['fields']['max_value']
            item_YD_YF_average_data = item['fields']['average_value']
            YD_YF_max_data_list.append(item_YD_YF_max_data)
            YD_YF_average_data_list.append(item_YD_YF_average_data)
    data_dit = {"month":month_data_list,"BGP_max_value":BGP_max_data_list,"BGP_average_value":BGP_average_data_list,"LT_max_value":LT_max_data_list,"LT_average_value":LT_average_data_list,"DX_max_value":DX_max_data_list,"DX_average_value":DX_average_data_list,"YD_YZ_max_value":YD_YZ_max_data_list,"YD_YZ_average_value":YD_YZ_average_data_list,"YD_YF_max_value":YD_YF_max_data_list,"YD_YF_average_value":YD_YF_average_data_list}

    return HttpResponse(json.dumps(data_dit))
    #return HttpResponse('ok')

#查询接口请求的区域统计数据
def get_area_api_data(request):

    month_data_list = []
    BJ_BGP_max_data_list = []
    BJ_BGP_average_data_list = []
    SH_BGP_max_data_list = []
    SH_BGP_average_data_list = []
    GZ_BGP_max_data_list = []
    GZ_BGP_average_data_list = []
    BJ_LT_max_data_list = []
    BJ_LT_average_data_list = []
    SH_LT_max_data_list = []
    SH_LT_average_data_list = []
    GZ_LT_max_data_list = []
    GZ_LT_average_data_list = []
    XA_LT_max_data_list = []
    XA_LT_average_data_list = []
    WH_LT_max_data_list = []
    WH_LT_average_data_list = []
    YZ_LT_max_data_list = []
    YZ_LT_average_data_list = []
    YF_LT_max_data_list = []
    YF_LT_average_data_list = []
    BJ_DX_max_data_list = []
    BJ_DX_average_data_list = []
    SH_DX_max_data_list = []
    SH_DX_average_data_list = []
    GZ_DX_max_data_list = []
    GZ_DX_average_data_list = []
    XA_DX_max_data_list = []
    XA_DX_average_data_list = []
    WH_DX_max_data_list = []
    WH_DX_average_data_list = []
    YZ_DX_max_data_list = []
    YZ_DX_average_data_list = []
    YF_DX_max_data_list = []
    YF_DX_average_data_list = []
    YZ_YD_max_data_list = []
    YZ_YD_average_data_list = []
    YF_YD_max_data_list = []
    YF_YD_average_data_list = []

    all_data = models.Area_month_count.objects.all().order_by('create_time')
    all_data_s = serializers.serialize("json", all_data)
    all_data_json = json.loads(all_data_s)
    last_data = models.Area_month_count.objects.all().order_by('-create_time')[0:1]
    last_data_s = serializers.serialize("json",last_data)
    last_data_json = json.loads(last_data_s)
    for item in all_data_json:
        last_month = item['fields']['month']
        last_month_s = str(last_month)

    for item in all_data_json:
        item_operator_data = item['fields']['operator']
        item_area_data = item['fields']['area']
        item_month_data = item['fields']['month']
        item_month_data_s = str(item_month_data)
        month_data_list.append(item_month_data)
        if item_operator_data == 'BGP' and item_area_data == 'BJ':
            item_BJ_BGP_max_data = item['fields']['max_value']
            item_BJ_BGP_average_data = item['fields']['average_value']
            BJ_BGP_max_data_list.append(item_BJ_BGP_max_data)
            BJ_BGP_average_data_list.append(item_BJ_BGP_average_data)
        elif item_operator_data == 'BGP' and item_area_data == 'SH':
            item_SH_BGP_max_data = item['fields']['max_value']
            item_SH_BGP_average_data = item['fields']['average_value']
            SH_BGP_max_data_list.append(item_SH_BGP_max_data)
            SH_BGP_average_data_list.append(item_SH_BGP_average_data)
        elif item_operator_data == 'BGP' and item_area_data == 'GZ':
            item_GZ_BGP_max_data = item['fields']['max_value']
            item_GZ_BGP_average_data = item['fields']['average_value']
            GZ_BGP_max_data_list.append(item_GZ_BGP_max_data)
            GZ_BGP_average_data_list.append(item_GZ_BGP_average_data)
        if item_month_data_s == last_month_s:
            if  item_operator_data == 'LT' and item_area_data == 'BJ':
                item_BJ_LT_max_data = item['fields']['max_value']
                item_BJ_LT_average_data = item['fields']['average_value']
                BJ_LT_max_data_list.append(item_BJ_LT_max_data)
                BJ_LT_average_data_list.append(item_BJ_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'SH':
                item_SH_LT_max_data = item['fields']['max_value']
                item_SH_LT_average_data = item['fields']['average_value']
                SH_LT_max_data_list.append(item_SH_LT_max_data)
                SH_LT_average_data_list.append(item_SH_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'GZ':
                item_GZ_LT_max_data = item['fields']['max_value']
                item_GZ_LT_average_data = item['fields']['average_value']
                GZ_LT_max_data_list.append(item_GZ_LT_max_data)
                GZ_LT_average_data_list.append(item_GZ_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'XA':
                item_XA_LT_max_data = item['fields']['max_value']
                item_XA_LT_average_data = item['fields']['average_value']
                XA_LT_max_data_list.append(item_XA_LT_max_data)
                XA_LT_average_data_list.append(item_XA_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'WH':
                item_WH_LT_max_data = item['fields']['max_value']
                item_WH_LT_average_data = item['fields']['average_value']
                WH_LT_max_data_list.append(item_WH_LT_max_data)
                WH_LT_average_data_list.append(item_WH_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'YZ':
                item_YZ_LT_max_data = item['fields']['max_value']
                item_YZ_LT_average_data = item['fields']['average_value']
                YZ_LT_max_data_list.append(item_YZ_LT_max_data)
                YZ_LT_average_data_list.append(item_YZ_LT_average_data)
            elif item_operator_data == 'LT' and item_area_data == 'YF':
                item_YF_LT_max_data = item['fields']['max_value']
                item_YF_LT_average_data = item['fields']['average_value']
                YF_LT_max_data_list.append(item_YF_LT_max_data)
                YF_LT_average_data_list.append(item_YF_LT_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'BJ':
                item_BJ_DX_max_data = item['fields']['max_value']
                item_BJ_DX_average_data = item['fields']['average_value']
                BJ_DX_max_data_list.append(item_BJ_DX_max_data)
                BJ_DX_average_data_list.append(item_BJ_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'SH':
                item_SH_DX_max_data = item['fields']['max_value']
                item_SH_DX_average_data = item['fields']['average_value']
                SH_DX_max_data_list.append(item_SH_DX_max_data)
                SH_DX_average_data_list.append(item_SH_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'GZ':
                item_GZ_DX_max_data = item['fields']['max_value']
                item_GZ_DX_average_data = item['fields']['average_value']
                GZ_DX_max_data_list.append(item_GZ_DX_max_data)
                GZ_DX_average_data_list.append(item_GZ_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'XA':
                item_XA_DX_max_data = item['fields']['max_value']
                item_XA_DX_average_data = item['fields']['average_value']
                XA_DX_max_data_list.append(item_XA_DX_max_data)
                XA_DX_average_data_list.append(item_XA_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'WH':
                item_WH_DX_max_data = item['fields']['max_value']
                item_WH_DX_average_data = item['fields']['average_value']
                WH_DX_max_data_list.append(item_WH_DX_max_data)
                WH_DX_average_data_list.append(item_WH_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'YZ':
                item_YZ_DX_max_data = item['fields']['max_value']
                item_YZ_DX_average_data = item['fields']['average_value']
                YZ_DX_max_data_list.append(item_YZ_DX_max_data)
                YZ_DX_average_data_list.append(item_YZ_DX_average_data)
            elif item_operator_data == 'DX' and item_area_data == 'YF':
                item_YF_DX_max_data = item['fields']['max_value']
                item_YF_DX_average_data = item['fields']['average_value']
                YF_DX_max_data_list.append(item_YF_DX_max_data)
                YF_DX_average_data_list.append(item_YF_DX_average_data)
            elif item_operator_data == 'YD' and item_area_data == 'YZ':
                item_YZ_YD_max_data = item['fields']['max_value']
                item_YZ_YD_average_data = item['fields']['average_value']
                YZ_YD_max_data_list.append(item_YZ_YD_max_data)
                YZ_YD_average_data_list.append(item_YZ_YD_average_data)
            elif item_operator_data == 'YD' and item_area_data == 'YF':
                item_YF_YD_max_data = item['fields']['max_value']
                item_YF_YD_average_data = item['fields']['average_value']
                YF_YD_max_data_list.append(item_YF_YD_max_data)
                YF_YD_average_data_list.append(item_YF_YD_average_data)

    data_dit = {"month": month_data_list,"last_month":last_month_s, "BJ_BGP_max_value": BJ_BGP_max_data_list,
                "BJ_BGP_average_value": BJ_BGP_average_data_list, "SH_BGP_max_value": SH_BGP_max_data_list,"SH_BGP_average_value":SH_BGP_average_data_list,"GZ_BGP_max_value":GZ_BGP_max_data_list,"GZ_BGP_average_value":GZ_BGP_average_data_list,"BJ_LT_max_value":BJ_LT_max_data_list,"BJ_LT_average_value":BJ_LT_average_data_list,"SH_LT_max_value":SH_LT_max_data_list,"SH_LT_average_value":SH_LT_average_data_list,"GZ_LT_max_value":GZ_LT_max_data_list,"GZ_LT_average_value":GZ_LT_average_data_list,"XA_LT_max_value":XA_LT_max_data_list,"XA_LT_average_value":XA_LT_average_data_list,"WH_LT_max_value":WH_LT_max_data_list,"WH_LT_average_value":WH_LT_average_data_list,"YZ_LT_max_value":YZ_LT_max_data_list,"YZ_LT_average_value":YZ_LT_average_data_list,"YF_LT_max_value":YF_LT_max_data_list,"YF_LT_average_value":YF_LT_average_data_list,"BJ_DX_max_value":BJ_DX_max_data_list,"BJ_DX_average_value":BJ_DX_average_data_list,"SH_DX_max_value":SH_DX_max_data_list,"SH_DX_average_value":SH_DX_average_data_list,"GZ_DX_max_value":GZ_DX_max_data_list,"GZ_DX_average_value":GZ_DX_average_data_list,"XA_DX_max_value":XA_DX_max_data_list,"XA_DX_average_value":XA_DX_average_data_list,"WH_DX_max_value":WH_DX_max_data_list,"WH_DX_average_value":WH_DX_average_data_list,"YZ_DX_max_value":YZ_DX_max_data_list,"YZ_DX_average_value":YZ_DX_average_data_list,"YF_DX_max_value":YF_DX_max_data_list,"YF_DX_average_value":YF_DX_average_data_list,"YZ_YD_max_value":YZ_YD_max_data_list,"YZ_YD_average_value":YZ_YD_average_data_list,"YF_YD_max_value":YF_YD_max_data_list,"YF_YD_average_value":YF_YD_average_data_list}

    return HttpResponse(json.dumps(data_dit))
    #return HttpResponse('ok')

#主页a链接运营商按月统计页面
def get_operator_month_count(request):

    return render_to_response('operator_traffic_month_count.html')

#主页a链接运营商按月统计页面
def get_area_month_count(request):

    return render_to_response('area_traffic_month_count.html')