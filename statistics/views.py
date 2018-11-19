# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response,redirect
# Create your views here.
from django.http.response import HttpResponse
from statistics import models
import MySQLdb
import json
import time
import rrdtool
import os,sys
from django.core import serializers

rrdpath = '/usr/local/apache2/htdocs/cacti/rra'

#获取host数据在前端页面显示
def index(request):
    try:
        conn = MySQLdb.connect(host='192.168.137.1',port=3306,user='root',passwd='123456',db='cacti')
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        data = cur.execute('select description from host')
        all_data = cur.fetchall()
        print all_data
        print type(all_data)

        cur.close()
        conn.close()
    except Exception,e:
        print e

    return render_to_response('index.html',{'data':all_data})

#设置分组的页面
def host_group(request):

    conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    data = cur.execute('select description from host where group_id is NULL')
    not_group_host_list = cur.fetchall()

    cur.close()
    conn.close()

    print not_group_host_list
    print type(not_group_host_list)

    group_name_list = models.Host_group.objects.all().values('group_name')

    #return render_to_response('host_group.html',{'group_name_list':group_name_list},{'not_group_host_list':not_group_host_list})
    return render_to_response('host_group.html',{'not_group_host_list': not_group_host_list,'group_name_list':group_name_list})

#创建分组的页面
def create_group(request):

    if request.method == 'GET':

        return render_to_response('create_group.html')

    if request.method == 'POST':

        group_name = request.POST.get('group_name')
        group_comment = request.POST.get('group_comment')

        group_name_is = models.Host_group.objects.filter(group_name=group_name)
        if group_name_is:
            return render_to_response('host_group.html')
        else:
            models.Host_group.objects.create(group_name=group_name,comment=group_comment)

        return render_to_response('host_group.html')

#删除分组的页面
def delete_group(request):

    return render_to_response('delete_group.html')

#添加主机到主机组
def add_host_to_group(request):

    if request.method == 'GET':

        conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        data = cur.execute('select description from host where group_id is NULL')
        not_group_host_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_to_response('add_host_to_group.html',{'not_group_host_list': not_group_host_list})

    if request.method == 'POST':

        group_name = request.POST.get('group_name')
        group_name_id = models.Host_group.objects.filter(group_name=group_name)
        group_name_id_s = serializers.serialize('json', group_name_id)
        group_name_id_json = json.loads(group_name_id_s)
        group_name_id_only = group_name_id_json[0]['pk']
        host_list = request.POST.getlist('group_to_host_list')

        conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = "update host set group_id = '{0}' where description = %s".format(group_name_id_only)
        data = cur.executemany(sql,host_list)

        cur.close()
        conn.close()

        return render_to_response('host_group.html')

#从主机组中删除主机
def del_host_from_group(request):

    return render_to_response('del_host_from_group.html')

#将页面传过来的数据进行计算，并将数据返给页面
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
        area = request.POST.get('area_data')
        area_str = area.encode('utf-8')
        service_line = request.POST.get('service_line_data')
        service_line_str = service_line.encode('utf-8')

        if operator_str == "selected":
            pass
        else:
            #查询传过来的运营商ID对应的运营商名字
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()

            sql = 'select operator from statistics_operator where id = %s'
            params = operator_str
            data = cur.execute(sql,params)
            operator_type = cur.fetchall()

            cur.close()
            conn.close()

            operator_type_str = str(operator_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')
            operator_type_str1 = "- "+operator_type_str

        if compute_str == "selected":
            pass
        else:
            #查询传过来的计算方法ID对应的计算方法
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()

            sql = 'select compute from statistics_compute where id = %s'
            params = compute_str
            data = cur.execute(sql, params)
            compute_type = cur.fetchall()

            cur.close()
            conn.close()

            compute_type_str = str(compute_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')


        if area_str == "selected":
            pass
        else:
            # 查询传过来的区域ID对应的区域名字
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()

            sql = 'select area from statistics_area where id = %s'
            params = area_str
            data = cur.execute(sql, params)
            area_type = cur.fetchall()

            cur.close()
            conn.close()

            area_type_str = str(area_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')

        if service_line_str == "selected":
            pass
        else:
            # 查询传过来的业务线ID对应的业务线名字
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()

            sql = 'select service_line from statistics_service_line where id = %s'
            params = service_line_str
            data = cur.execute(sql, params)
            service_line_type = cur.fetchall()

            cur.close()
            conn.close()

            service_line_type_str = str(service_line_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')

        # 查询根据Traffic加上主机名和运营商找到对应的rrd文件路径的数据
        rrd_file_list = []
        for item in host:
            item_str = item.encode('utf-8')

            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor()
    
            sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(item_str,operator_type_str1)
            data = cur.execute(sql)
            rrd = cur.fetchall()

            cur.close()
            conn.close()

            rrd = rrd.__str__()
            rrd_file_path = rrd.replace('<path_rra>',rrdpath).strip('(').strip(')').strip(',').strip("'").strip(')').strip(',').strip("'").encode('utf-8')
            rrd_file_list.append(rrd_file_path)

        # 通过rrdtool查询rrd数据
        fetch_result_list = []
        fetch_result_list_max = []
        fetch_result_list_average = []
        if compute_type_str == 'ALL':
            for item in rrd_file_list:
                start_time_stamp_rrd = str('-s'+' '+start_time_stamp)
                end_time_stamp_rrd = str('-e'+' '+end_time_stamp)
                fetch_result_max = rrdtool.fetch(item,str('MAX'),start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list_max.append(fetch_result_max)
                fetch_result_average = rrdtool.fetch(item,str('AVERAGE'),start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list_average.append(fetch_result_average)

            print fetch_result_list_max
            #print fetch_result_list_average
        else:
            for item in rrd_file_list:
                start_time_stamp_rrd = str('-s'+' '+start_time_stamp)
                end_time_stamp_rrd = str('-e'+' '+end_time_stamp)
                fetch_result = rrdtool.fetch(item,compute_type_str,start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list.append(fetch_result)

            print fetch_result_list

        traffic_list = []
        traffic_list_count = []
        traffic_list_MAX = []
        traffic_list_AVERAGE = []
        traffic_list_count_MAX = []
        traffic_list_count_AVERAGE = []
        # 将None的数据替换为0，将rrdtool算出来的数据做max和average的运算
        if compute_type_str == 'ALL':
            for item in fetch_result_list_max:
                for items in item[2]:
                    if items[0] is None and items[1] is None:
                        traffic = float(0)
                    elif items[0] > items[1]:
                        traffic = items[0] * 8
                    elif items[0] < items[1]:
                        traffic = items[1] * 8
                    else:
                        traffic = items[0] * 8
                    traffic_list_MAX.append(traffic)
                traffic_max = round(max(traffic_list_MAX) / float(1024) / float(1024), 2)
                traffic_list_count_MAX.append(traffic_max)
                traffic_list_MAX = []

            print sum(traffic_list_count_MAX)
            traffic_list_count_MAX_sum = sum(traffic_list_count_MAX)

            for item in fetch_result_list_average:
                for items in item[2]:
                    if items[0] is None and items[1] is None:
                        traffic = float(0)
                    elif items[0] > items[1]:
                        traffic = items[0] * 8
                    elif items[0] < items[1]:
                        traffic = items[1] * 8
                    else:
                        traffic = items[0] * 8
                    traffic_list_AVERAGE.append(traffic)
                traffic_sum = sum(traffic_list_AVERAGE)
                traffic_list_len = float(len(traffic_list_AVERAGE))
                traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024), 2)
                traffic_list_count_AVERAGE.append(traffic_average)
                traffic_list_AVERAGE = []

            print sum(traffic_list_count_AVERAGE)
            traffic_list_count_AVERAGE_sum = sum(traffic_list_count_AVERAGE)
        else:

            for item in fetch_result_list:
                for items in item[2]:
                    if items[0] is None and items[1] is None:
                        traffic = float(0)
                    elif items[0] > items[1]:
                        traffic = items[0]*8
                    elif items[0] < items[1]:
                        traffic = items[1]*8
                    else:
                        traffic = items[0]*8
                    traffic_list.append(traffic)
                if compute_type_str == 'MAX':
                    traffic_max = round(max(traffic_list) / float(1024) / float(1024), 2)
                    traffic_list_count.append(traffic_max)
                    traffic_list = []
                elif compute_type_str == 'AVERAGE':
                    traffic_sum = sum(traffic_list)
                    traffic_list_len = float(len(traffic_list))
                    traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024), 2)
                    traffic_list_count.append(traffic_average)
                    traffic_list = []
                
            print sum(traffic_list_count)
            traffic_list_count_sum = sum(traffic_list_count)

        if area_str == "selected" and service_line_str == "selected":
            #按运营商进行的流量数据统计
            print 'operator'
            if compute_type_str == "ALL":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            elif compute_type_str == "MAX":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=traffic_list_count_sum,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=None,average_value=traffic_list_count_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            else:
                print "no data"
        elif service_line_str == "selected":
            #按区域进行的流量数据统计
            print 'area'
            if compute_type_str == "ALL":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            elif compute_type_str == "MAX":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=traffic_list_count_sum,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=None,average_value=traffic_list_count_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            else:
                print "no data"
        elif area_str == "selected":
            #按业务线进行的流量数据统计
            print 'service_line'
            if compute_type_str == "ALL":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('service_line_traffic.html')
            elif compute_type_str == "MAX":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=traffic_list_count_sum,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('service_line_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=None,average_value=traffic_list_count_sum,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('service_line_traffic.html')
            else:
                print "no data"
        else:
            pass

    return HttpResponse('aaa')

#用于ajax查询运营商数据在前端页面显示
def show_operator(request):

    if request.method == 'GET':

        try:
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
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
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

            data = cur.execute('select * from statistics_compute')
            all_data = cur.fetchall()

            cur.close()
            conn.close()
        except Exception, e:
            print e

    return HttpResponse(json.dumps(all_data))

#用于ajax查询区域在前端页面显示
def show_area(request):

    if request.method == 'GET':

        try:
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

            data = cur.execute('select * from statistics_area')
            all_data = cur.fetchall()

            cur.close()
            conn.close()
        except Exception, e:
            print e

    return HttpResponse(json.dumps(all_data))

#用于ajax查询业务线在前端页面显示
def show_service_line(request):

    if request.method == 'GET':

        try:
            conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

            data = cur.execute('select * from statistics_service_line')
            all_data = cur.fetchall()

            cur.close()
            conn.close()
        except Exception, e:
            print e

    return HttpResponse(json.dumps(all_data))

#存储运营商月统计的流量数据
def handle_api(request,date,host,operator,compute,area):

    print date,host,operator,compute,area

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
    print year_s
    print month_s
    if month_s.startswith('0'):
        month_s = month_s[1:]
    if int(month_s) in da:
        day_s = '31'
    elif int(month_s) in xiao:
        day_s = '30'
    else:
        if int(year_s) % 400 == 0 or (int(year_s) % 4 == 0 and int(year_s) % 100 != 0):
            day_s = '29'
        else:
            day_s = '28'
    start_time = year_s+'-'+month_s+'-'+'1'+' '+start_time_h
    end_time = year_s+'-'+month_s+'-'+day_s+' '+end_time_h
    start_timestamp = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    start_timestamp = str(int(time.mktime(start_timestamp)))
    end_timestamp = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    end_timestamp = str(int(time.mktime(end_timestamp)))
    host_list = host.split('+')
    operator_1 = '- '+operator.encode('utf-8')
    area_s = area.encode('utf-8')
    print start_timestamp
    print end_timestamp

    rrd_file_list = []
    for item in host_list:
        item_str = item.encode('utf-8')

        conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        rrd = cur.fetchall()

        cur.close()
        conn.close()

        rrd = rrd.__str__()
        rrd_file_path = rrd.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
            ')').strip(',').strip("'").encode('utf-8')
        rrd_file_list.append(rrd_file_path)

    fetch_result_list_max = []
    fetch_result_list_average = []
    for item in rrd_file_list:
        fetch_result_max = rrdtool.fetch(item, str('MAX'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_max.append(fetch_result_max)
        fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_average.append(fetch_result_average)
        print fetch_result_list_max
        print fetch_result_list_average

    traffic_list_MAX = []
    traffic_list_AVERAGE = []
    traffic_list_count_MAX = []
    traffic_list_count_AVERAGE = []
    for item in fetch_result_list_max:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_MAX.append(traffic)
        traffic_max = round(max(traffic_list_MAX) / float(1024) / float(1024), 2)
        traffic_list_count_MAX.append(traffic_max)
        traffic_list_MAX = []

    traffic_list_count_MAX_sum = sum(traffic_list_count_MAX)

    for item in fetch_result_list_average:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_AVERAGE.append(traffic)
        traffic_sum = sum(traffic_list_AVERAGE)
        traffic_list_len = float(len(traffic_list_AVERAGE))
        traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024), 2)
        traffic_list_count_AVERAGE.append(traffic_average)
        traffic_list_AVERAGE = []

    traffic_list_count_AVERAGE_sum = sum(traffic_list_count_AVERAGE)

    models.Operator_month_count.objects.create(operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum,comment=area_s)

    return HttpResponse('ok')

#存储区域月统计的流量数据
def handle_area_api(request,date,host,operator,compute,area):

    print date,host,operator,compute,area

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
    print year_s
    print month_s
    if month_s.startswith('0'):
        month_s = month_s[1:]
    if int(month_s) in da:
        day_s = '31'
    elif int(month_s) in xiao:
        day_s = '30'
    else:
        if int(year_s) % 400 == 0 or (int(year_s) % 4 == 0 and int(year_s) % 100 != 0):
            day_s = '29'
        else:
            day_s = '28'
    start_time = year_s+'-'+month_s+'-'+'1'+' '+start_time_h
    end_time = year_s+'-'+month_s+'-'+day_s+' '+end_time_h
    start_timestamp = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    start_timestamp = str(int(time.mktime(start_timestamp)))
    end_timestamp = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    end_timestamp = str(int(time.mktime(end_timestamp)))
    host_list = host.split('+')
    operator_1 = '- '+operator.encode('utf-8')
    area_s = area.encode('utf-8')

    rrd_file_list = []
    for item in host_list:
        item_str = item.encode('utf-8')

        conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        rrd = cur.fetchall()

        cur.close()
        conn.close()

        rrd = rrd.__str__()
        rrd_file_path = rrd.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
            ')').strip(',').strip("'").encode('utf-8')
        rrd_file_list.append(rrd_file_path)

    fetch_result_list_max = []
    fetch_result_list_average = []
    for item in rrd_file_list:
        fetch_result_max = rrdtool.fetch(item, str('MAX'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_max.append(fetch_result_max)
        fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_average.append(fetch_result_average)

    traffic_list_MAX = []
    traffic_list_AVERAGE = []
    traffic_list_count_MAX = []
    traffic_list_count_AVERAGE = []
    for item in fetch_result_list_max:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_MAX.append(traffic)
        traffic_max = round(max(traffic_list_MAX) / float(1024) / float(1024), 2)
        traffic_list_count_MAX.append(traffic_max)
        traffic_list_MAX = []

    traffic_list_count_MAX_sum = sum(traffic_list_count_MAX)

    for item in fetch_result_list_average:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_AVERAGE.append(traffic)
        traffic_sum = sum(traffic_list_AVERAGE)
        traffic_list_len = float(len(traffic_list_AVERAGE))
        traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024), 2)
        traffic_list_count_AVERAGE.append(traffic_average)
        traffic_list_AVERAGE = []

    traffic_list_count_AVERAGE_sum = sum(traffic_list_count_AVERAGE)

    models.Area_month_count.objects.create(area=area_s,operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum)

    return HttpResponse('ok')

#存储业务线统计的流量数据
def handle_service_line_api(request,date,host,operator,compute,area,service_line):

    print date,host,operator,compute,area,service_line

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
    print year_s
    print month_s
    if month_s.startswith('0'):
        month_s = month_s[1:]
    if int(month_s) in da:
        day_s = '31'
    elif int(month_s) in xiao:
        day_s = '30'
    else:
        if int(year_s) % 400 == 0 or (int(year_s) % 4 == 0 and int(year_s) % 100 != 0):
            day_s = '29'
        else:
            day_s = '28'
    start_time = year_s+'-'+month_s+'-'+'1'+' '+start_time_h
    end_time = year_s+'-'+month_s+'-'+day_s+' '+end_time_h
    start_timestamp = time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
    start_timestamp = str(int(time.mktime(start_timestamp)))
    end_timestamp = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    end_timestamp = str(int(time.mktime(end_timestamp)))
    host_list = host.split('+')
    operator_1 = '- '+operator.encode('utf-8')
    area_s = area.encode('utf-8')
    service_line_s = service_line.encode('utf-8')

    rrd_file_list = []
    for item in host_list:
        item_str = item.encode('utf-8')

        conn = MySQLdb.connect(host='192.168.137.1', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        rrd = cur.fetchall()

        cur.close()
        conn.close()

        rrd = rrd.__str__()
        rrd_file_path = rrd.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
            ')').strip(',').strip("'").encode('utf-8')
        rrd_file_list.append(rrd_file_path)

    fetch_result_list_max = []
    fetch_result_list_average = []
    for item in rrd_file_list:
        fetch_result_max = rrdtool.fetch(item, str('MAX'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_max.append(fetch_result_max)
        fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), str('-s' + ' ' + start_timestamp), str('-e' + ' ' + end_timestamp))
        fetch_result_list_average.append(fetch_result_average)

    traffic_list_MAX = []
    traffic_list_AVERAGE = []
    traffic_list_count_MAX = []
    traffic_list_count_AVERAGE = []
    for item in fetch_result_list_max:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_MAX.append(traffic)
        traffic_max = round(max(traffic_list_MAX) / float(1024) / float(1024), 2)
        traffic_list_count_MAX.append(traffic_max)
        traffic_list_MAX = []

    traffic_list_count_MAX_sum = sum(traffic_list_count_MAX)

    for item in fetch_result_list_average:
        for items in item[2]:
            if items[0] is None and items[1] is None:
                traffic = float(0)
            elif items[0] > items[1]:
                traffic = items[0] * 8
            elif items[0] < items[1]:
                traffic = items[1] * 8
            else:
                traffic = items[0] * 8
            traffic_list_AVERAGE.append(traffic)
        traffic_sum = sum(traffic_list_AVERAGE)
        traffic_list_len = float(len(traffic_list_AVERAGE))
        traffic_average = round(traffic_sum / traffic_list_len / float(1024) / float(1024), 2)
        traffic_list_count_AVERAGE.append(traffic_average)
        traffic_list_AVERAGE = []

    traffic_list_count_AVERAGE_sum = sum(traffic_list_count_AVERAGE)

    models.Service_line_month_count.objects.create(service_line=service_line_s,area=area_s,operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum)

    return HttpResponse('ok')