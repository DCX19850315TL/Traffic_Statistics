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
    max_data_list = []
    average_data_list = []
    all_data = models.Operator_month_count.objects.all().order_by('create_time')
    all_data_s = serializers.serialize("json",all_data)
    all_data_json = json.loads(all_data_s)
    for item in all_data_json:
        item_month_data = item['fields']['month']
        item_max_data = item['fields']['max_value']
        item_average_data = item['fields']['average_value']
        month_data_list.append(item_month_data)
        max_data_list.append(item_max_data)
        average_data_list.append(item_average_data)
    data_dit = {"month":month_data_list,"max_value":max_data_list,"average_value":average_data_list}

    return HttpResponse(json.dumps(data_dit))

def get_operator_month_count(request):

    return render_to_response('operator_traffic_month_count.html')