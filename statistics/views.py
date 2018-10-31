# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response
# Create your views here.
from django.http.response import HttpResponse
from statistics import models
import MySQLdb
import json
import time
import rrdtool
import os,sys

rrdpath = '/usr/local/apache2/htdocs/cacti/rra'


def index(request):
    try:
        conn = MySQLdb.connect(host='10.160.92.77',port=3306,user='root',passwd='123456',db='cacti')
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        data = cur.execute('select description from host')
        all_data = cur.fetchall()
        print all_data

        cur.close()
        conn.close()
    except Exception,e:
        print e

    return render_to_response('index.html',{'data':all_data})

def handle(request):

    if request.method == 'POST':

        print request.POST

        host = request.POST.getlist('host_data_out')
        #host_str = host.encode('utf-8')
        operator = request.POST.get('operator_data')
        operator_str = operator.encode('utf-8')
        start_time = request.POST.get('start_time')
        start_time_str = start_time.encode('utf-8').replace('T',' ')
        end_time = request.POST.get('end_time')
        end_time_str = end_time.encode('utf-8').replace('T',' ')
        start_time_stamp = time.strptime(start_time_str,"%Y-%m-%d %H:%M:%S")
        start_time_stamp = str(int(time.mktime(start_time_stamp)))
        end_time_stamp = time.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
        end_time_stamp = str(int(time.mktime(end_time_stamp)))
        compute = request.POST.get('compute_data')
        compute_str = compute.encode('utf-8')

        print host

        #查询传过来的运营商ID对应的运营商名字
        conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = 'select operator from statistics_operator where id = %s'
        params = operator_str
        data = cur.execute(sql,params)
        operator_type = cur.fetchall()

        cur.close()
        conn.close()

        operator_type_str = str(operator_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')
        operator_type_str1 = "- "+operator_type_str

        #查询传过来的计算方法ID对应的计算方法
        conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = 'select compute from statistics_compute where id = %s'
        params = compute_str
        data = cur.execute(sql, params)
        compute_type = cur.fetchall()

        cur.close()
        conn.close()

        compute_type_str = str(compute_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')

        rrd_file_list = []
        for item in host:
            item_str = item.encode('utf-8')

            #查询根据Traffic加上主机名和运营商找到对应的rrd文件路径的数据
            conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()
    
            sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(item_str,operator_type_str1)
            data = cur.execute(sql)
            rrd = cur.fetchall()

            cur.close()
            conn.close()

            rrd = rrd.__str__()
            rrd_file_path = rrd.replace('<path_rra>',rrdpath).strip('(').strip(')').strip(',').strip("'").strip(')').strip(',').strip("'").encode('utf-8')
            rrd_file_list.append(rrd_file_path)

        #print rrd_file_list

        fetch_result_list = []
        for item in rrd_file_list:
            #通过rrdtool查询rrd数据
            start_time_stamp_rrd = str('-s'+' '+start_time_stamp)
            end_time_stamp_rrd = str('-e'+' '+end_time_stamp)
            #print start_time_stamp_rrd
            #print end_time_stamp_rrd
            fetch_result = rrdtool.fetch(item,compute_type_str,start_time_stamp_rrd,end_time_stamp_rrd)
            fetch_result_list.append(fetch_result)
            #print fetch_result
            #print type(fetch_result)
        #print fetch_result_list
        #print fetch_result_list[0][2]

        for item in fetch_result_list:
            for items in item[2]:
                print items
        '''
        #将None的数据替换为0，将rrdtool算出来的数据做max和average的运算
        traffic_list = []
        for item in fetch_result[2]:
            if item[0] is None and item[1] is None:
                traffic = float(0)
            elif item[0] > item[1]:
                traffic = item[0]*8
            elif item[0] < item[1]:
                traffic = item[1]*8
            else:
                traffic = item[0]*8
            traffic_list.append(traffic)
        print traffic_list
        traffic_max = round(max(traffic_list) / float(1024) / float(1024),2)
        print traffic_max
        traffic_sum = sum(traffic_list)
        traffic_list_len = float(len(traffic_list))
        traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024),2)
        print traffic_sum
        print traffic_list_len
        print traffic_average
        '''
    return HttpResponse('aaa')

#用于ajax查询运营商数据在前端页面显示
def show_operator(request):

    if request.method == 'GET':

        try:
            conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

            data = cur.execute('select * from statistics_operator')
            all_data = cur.fetchall()

            cur.close()
            conn.close()
        except Exception, e:
            print e

    return HttpResponse(json.dumps(all_data))

#用于ajax查询计算方法在前端页面显示
def show_compute(request):

    if request.method == 'GET':

        try:
            conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

            data = cur.execute('select * from statistics_compute')
            all_data = cur.fetchall()

            cur.close()
            conn.close()
        except Exception, e:
            print e

    return HttpResponse(json.dumps(all_data))