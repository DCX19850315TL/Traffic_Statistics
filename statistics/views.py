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
from common.logger import logger
from Traffic_Statistics.settings import RRD_PATH,DATABASES
#配置rrd文件夹路径的变量
rrdpath = RRD_PATH
#配置数据库的相应变量
DB_HOST = DATABASES['default']['HOST']
DB_PORT = int(DATABASES['default']['PORT'])
DB_USER = DATABASES['default']['USER']
DB_PASSWORD = DATABASES['default']['PASSWORD']
DB_DATABASE = DATABASES['default']['NAME']
#配置日志文件存放目录的变量
Logger_Info_File = logger('INFO')
Logger_Error_File = logger('ERROR')

#获取host数据在前端页面显示
def index(request):
    try:
        conn = MySQLdb.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,passwd=DB_PASSWORD,db=DB_DATABASE)
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        data = cur.execute('select description from host')
        all_data = cur.fetchall()

        cur.close()
        conn.close()

        group_name_list = models.Host_group.objects.all().values('group_name')

    except Exception,e:
        print e

    return render_to_response('index.html', {'data':all_data, 'group_name_list':group_name_list})
    #return render_to_response('index.bak.html', {'data': all_data})

#设置分组的页面
def host_group(request):

    conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
    cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    data = cur.execute('select description from host where group_id is NULL')
    not_group_host_list = cur.fetchall()

    cur.close()
    conn.close()

    group_name_list = models.Host_group.objects.all().values('group_name')

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

#添加主机到主机组a
def add_host_to_group(request):

    if request.method == 'GET':

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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

        host_data_out = request.POST.getlist('host_data_out')
        if host_data_out:
            host = request.POST.getlist('host_data_out')
        else:
            host = request.POST.getlist('group_to_host_list')
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
            cur = conn.cursor()

            sql = 'select compute from statistics_compute where id = %s'
            params = compute_str
            data = cur.execute(sql, params)
            compute_type = cur.fetchall()

            cur.close()
            conn.close()

            compute_type_str = str(compute_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')


        if area_str == "0":
            pass
        else:
            # 查询传过来的区域ID对应的区域名字
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
            cur = conn.cursor()

            sql = 'select area from statistics_area where id = %s'
            params = area_str
            data = cur.execute(sql, params)
            area_type = cur.fetchall()

            cur.close()
            conn.close()

            area_type_str = str(area_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')

        if service_line_str == "0":
            pass
        else:
            # 查询传过来的业务线ID对应的业务线名字
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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

            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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
        fetch_result_dict_count = {}
        fetch_result_dict_count_max = {}
        fetch_result_dict_count_average = {}

        if compute_type_str == 'ALL':
            for item in rrd_file_list:
                start_time_stamp_rrd = str('-s'+' '+start_time_stamp)
                end_time_stamp_rrd = str('-e'+' '+end_time_stamp)
                fetch_result_max = rrdtool.fetch(item,str('MAX'),start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list_max.append(fetch_result_max)
                fetch_result_average = rrdtool.fetch(item,str('AVERAGE'),start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list_average.append(fetch_result_average)
                fetch_result_dict_max = {item: fetch_result_max}
                fetch_result_dict_count_max.update(fetch_result_dict_max)
                fetch_result_dict_average = {item: fetch_result_average}
                fetch_result_dict_count_average.update(fetch_result_dict_average)
        else:
            for item in rrd_file_list:
                start_time_stamp_rrd = str('-s'+' '+start_time_stamp)
                end_time_stamp_rrd = str('-e'+' '+end_time_stamp)
                fetch_result = rrdtool.fetch(item,compute_type_str,start_time_stamp_rrd,end_time_stamp_rrd)
                fetch_result_list.append(fetch_result)
                fetch_result_dict = {item:fetch_result}
                fetch_result_dict_count.update(fetch_result_dict)

        # 将每个主机的流量添加到一个新的列表
        traffic_count_list = []
        traffic_count_list_max = []
        traffic_count_list_average = []
        for k,v in fetch_result_dict_count.items():
            traffic_count_list.append(v[2])
        for k,v in fetch_result_dict_count_max.items():
            traffic_count_list_max.append(v[2])
        for k,v in fetch_result_dict_count_average.items():
            traffic_count_list_average.append(v[2])


        # 每台主机列表的个数和总共的列表个数
        if compute_type_str == 'ALL':
            list_num = len(traffic_count_list_max[0])
            list_count_num = len(traffic_count_list_max)
        else:
            list_num = len(traffic_count_list[0])
            list_count_num = len(traffic_count_list)

        # 将进出流量的大值放到新的列表中
        traffic_list_new = []
        traffic_list_new2 = []
        traffic_list_new_max = []
        traffic_list_new2_max = []
        traffic_list_new_average = []
        traffic_list_new2_average = []
        if compute_type_str == 'ALL':
            for i in range(list_count_num):
                for j in range(list_num):
                    traffic_in = traffic_count_list_max[i][j][0]
                    traffic_out = traffic_count_list_max[i][j][1]
                    if traffic_in is None and traffic_out is None:
                        traffic_list_new_max.append(float(0))
                    elif traffic_in > traffic_out:
                        traffic_list_new_max.append(traffic_in)
                    else:
                        traffic_list_new_max.append(traffic_out)
                    traffic_dit = {i: traffic_list_new_max}

                traffic_list_new2_max.append(traffic_dit)
                traffic_list_new_max = []

            for i in range(list_count_num):
                for j in range(list_num):
                    traffic_in = traffic_count_list_average[i][j][0]
                    traffic_out = traffic_count_list_average[i][j][1]
                    if traffic_in is None and traffic_out is None:
                        traffic_list_new_average.append(float(0))
                    elif traffic_in > traffic_out:
                        traffic_list_new_average.append(traffic_in)
                    else:
                        traffic_list_new_average.append(traffic_out)
                    traffic_dit = {i: traffic_list_new_average}

                traffic_list_new2_average.append(traffic_dit)
                traffic_list_new_average = []
        else:
            for i in range(list_count_num):
                for j in range(list_num):
                    traffic_in = traffic_count_list[i][j][0]
                    traffic_out = traffic_count_list[i][j][1]
                    if traffic_in is None and traffic_out is None:
                        traffic_list_new.append(float(0))
                    elif traffic_in > traffic_out:
                        traffic_list_new.append(traffic_in)
                    else:
                        traffic_list_new.append(traffic_out)
                    traffic_dit={i:traffic_list_new}

                traffic_list_new2.append(traffic_dit)
                traffic_list_new = []

        # 按顺序将每台主机的同一行的数据放到一个新的列表
        traffic_list_new3 = []
        traffic_list_new4 = []
        traffic_list_new3_max = []
        traffic_list_new4_max = []
        traffic_list_new3_average = []
        traffic_list_new4_average = []
        if compute_type_str == 'ALL':
            for i in range(list_num):
                for j in range(list_count_num):
                    traffic_0 = traffic_list_new2_max[j][j][i]
                    traffic_list_new3_max.append(traffic_0)
                traffic_dit2 = {i: traffic_list_new3_max}
                traffic_list_new3_max = []
                traffic_list_new4_max.append(traffic_dit2)

            for i in range(list_num):
                for j in range(list_count_num):
                    traffic_0 = traffic_list_new2_average[j][j][i]
                    traffic_list_new3_average.append(traffic_0)
                traffic_dit2 = {i: traffic_list_new3_average}
                traffic_list_new3_average = []
                traffic_list_new4_average.append(traffic_dit2)
        else:
            for i in range(list_num):
                for j in range(list_count_num):
                    traffic_0 = traffic_list_new2[j][j][i]
                    traffic_list_new3.append(traffic_0)
                traffic_dit2={i:traffic_list_new3}
                traffic_list_new3 = []
                traffic_list_new4.append(traffic_dit2)

        # 将所有主机的同一条数据进行加运算后放到最终的列表中
        traffic_list_new5 = []
        traffic_list_new5_max = []
        traffic_list_new5_average = []
        if compute_type_str == 'ALL':
            for i in range(list_num):
                traffic_1 = traffic_list_new4_max[i][i]
                traffic_1_sum = sum(traffic_1)
                traffic_list_new5_max.append(traffic_1_sum)

            for i in range(list_num):
                traffic_1 = traffic_list_new4_average[i][i]
                traffic_1_sum = sum(traffic_1)
                traffic_list_new5_average.append(traffic_1_sum)
        else:
            for i in range(list_num):
                traffic_1 = traffic_list_new4[i][i]
                traffic_1_sum = sum(traffic_1)
                traffic_list_new5.append(traffic_1_sum)

        # 将None的数据替换为0，将rrdtool算出来的数据做max和average的运算
        if compute_type_str == 'ALL':
            traffic_max = round(max(traffic_list_new5_max) * 8 / float(1024) / float(1024), 2)

            traffic_new5_sum = sum(traffic_list_new5_average)
            traffic_new5_len = float(len(traffic_list_new5_average))
            traffic_average = round(traffic_new5_sum / traffic_new5_len * 8 / float(1024) / float(1024), 2)
        else:
            if compute_type_str == 'MAX':
                traffic_max = round(max(traffic_list_new5) * 8 / float(1024) / float(1024), 2)
            elif compute_type_str == 'AVERAGE':
                traffic_new5_sum = sum(traffic_list_new5)
                traffic_new5_len = float(len(traffic_list_new5))
                traffic_average = round(traffic_new5_sum / traffic_new5_len * 8 / float(1024) / float(1024), 2)

        if area_str == "0" and service_line_str == "0":
            #按运营商进行的流量数据统计
            print 'operator'
            if compute_type_str == "ALL":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=traffic_max,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            elif compute_type_str == "MAX":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=traffic_max,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Operator_compute_result.objects.create(operator=operator_type_str,max_value=None,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('operator_traffic.html')
            else:
                print "no data"
        elif service_line_str == "0":
            #按区域进行的流量数据统计
            print 'area'
            if compute_type_str == "ALL":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=traffic_max,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            elif compute_type_str == "MAX":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=traffic_max,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Area_compute_result.objects.create(area=area_type_str,operator=operator_type_str,max_value=None,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('area_traffic.html')
            else:
                print "no data"
        elif area_str == "0":
            #按业务线进行的流量数据统计
            print 'service_line'
            if compute_type_str == "ALL":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=traffic_max,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('service_line_traffic.html')
            elif compute_type_str == "MAX":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=traffic_max,average_value=None,start_time=start_time_str,end_time=end_time_str)
                return render_to_response('service_line_traffic.html')
            elif compute_type_str == "AVERAGE":
                models.Service_line_compute_result.objects.create(service_line=service_line_type_str,operator=operator_type_str,max_value=None,average_value=traffic_average,start_time=start_time_str,end_time=end_time_str)
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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
            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
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

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        if data == 0:
            continue
        elif data == 1:
            rrd = cur.fetchall()
        elif data == 2:
            rrd = cur.fetchall()

        cur.close()
        conn.close()

        for item in rrd:
            rrd_item = item.__str__()
            rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(')').strip(',').strip("'").encode('utf-8')
            if os.path.exists(rrd_file_path):
                rrd_file_list.append(rrd_file_path)
            else:
                continue

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

    models.Operator_month_count.objects.create(operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_list_count_MAX_sum,average_value=traffic_list_count_AVERAGE_sum,comment=area_s)

    return HttpResponse('ok')

#存储区域月统计的流量数据
def handle_area_api(request,date,host,operator,compute,area):

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        if data == 0:
            continue
        elif data == 1:
            rrd = cur.fetchall()
        elif data == 2:
            rrd = cur.fetchall()

        cur.close()
        conn.close()

        for item in rrd:
            rrd_item = item.__str__()
            rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
                ')').strip(',').strip("'").encode('utf-8')
            if os.path.exists(rrd_file_path):
                rrd_file_list.append(rrd_file_path)
            else:
                continue

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

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        if data == 0:
            continue
        elif data == 1:
            rrd = cur.fetchall()
        elif data == 2:
            rrd = cur.fetchall()

        cur.close()
        conn.close()

        for item in rrd:
            rrd_item = item.__str__()
            rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
                ')').strip(',').strip("'").encode('utf-8')
            if os.path.exists(rrd_file_path):
                rrd_file_list.append(rrd_file_path)
            else:
                continue

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

#存储运营商月统计的流量数据_NEW
def handle_api_new(request,date,host,operator,compute,area):

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1, 3, 5, 7, 8, 10, 12]
    xiao = [4, 6, 9, 11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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
    start_time = year_s + '-' + month_s + '-' + '1' + ' ' + start_time_h
    end_time = year_s + '-' + month_s + '-' + day_s + ' ' + end_time_h
    start_timestamp = time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    start_timestamp = str(int(time.mktime(start_timestamp)))
    end_timestamp = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    end_timestamp = str(int(time.mktime(end_timestamp)))
    host_list = host.split('+')
    operator_1 = '- ' + operator.encode('utf-8')
    area_s = area.encode('utf-8')
    
    #根据条件将所有的rrd文件进行汇总
    try:
        rrd_file_list = []
        for item in host_list:
            item_str = item.encode('utf-8')

            conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
            cur = conn.cursor()

            sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
                item_str, operator_1)
            data = cur.execute(sql)
            if data == 0:
                continue
            elif data == 1:
                rrd = cur.fetchall()
            elif data == 2:
                rrd = cur.fetchall()

            cur.close()
            conn.close()

            for item in rrd:
                rrd_item = item.__str__()
                rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
                    ')').strip(',').strip("'").encode('utf-8')
                if os.path.exists(rrd_file_path):
                    rrd_file_list.append(rrd_file_path)
                else:
                    Logger_Error_File.exception('%s该rrd文件不存在' % (rrd_file_path))
                    continue
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        # 通过rrdtool查询rrd数据
        fetch_result_list = []
        fetch_result_list_max = []
        fetch_result_list_average = []
        fetch_result_dict_max_count = {}
        fetch_result_dict_average_count = {}
        for item in rrd_file_list:
            start_time_stamp_rrd = str('-s' + ' ' + start_timestamp)
            end_time_stamp_rrd = str('-e' + ' ' + end_timestamp)
            fetch_result_max = rrdtool.fetch(item, str('MAX'), start_time_stamp_rrd, end_time_stamp_rrd)
            fetch_result_list_max.append(fetch_result_max)
            fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), start_time_stamp_rrd, end_time_stamp_rrd)
            fetch_result_list_average.append(fetch_result_average)
            fetch_result_dict_max = {item: fetch_result_max}
            fetch_result_dict_max_count.update(fetch_result_dict_max)
            fetch_result_dict_average = {item: fetch_result_average}
            fetch_result_dict_average_count.update(fetch_result_dict_average)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        #将每个主机的流量添加到一个新的列表
        traffic_count_list_max = []
        for k, v in fetch_result_dict_max_count.items():
            traffic_count_list_max.append(v[2])
        traffic_count_list_average = []
        for k, v in fetch_result_dict_average_count.items():
            traffic_count_list_average.append(v[2])
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        data_len_list = []
        for item in range(len(traffic_count_list_max)):
            data = len(traffic_count_list_max[item])
            data_len_list.append(data)

        def max_list(lt):
            temp = 0
            for i in lt:
                if lt.count(i) > temp:
                    max_str = i
                    temp = lt.count(i)
            return max_str

        if len(traffic_count_list_max) == 1:
            list_num = len(traffic_count_list_max[0])
        else:
            list_num = max_list(data_len_list)
        # 总共的列表个数
        list_count_num = len(traffic_count_list_max)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        #将进出流量的大值放到新的列表中
        traffic_list_new_max = []
        traffic_list_new2_max = []
        for i in range(list_count_num):
            for j in range(list_num):
                traffic_in = traffic_count_list_max[i][j][0]
                traffic_out = traffic_count_list_max[i][j][1]
                if traffic_in is None and traffic_out is None:
                    traffic_list_new_max.append(float(0))
                elif traffic_in > traffic_out:
                    traffic_list_new_max.append(traffic_in)
                else:
                    traffic_list_new_max.append(traffic_out)
                traffic_dit = {i: traffic_list_new_max}

            traffic_list_new2_max.append(traffic_dit)
            traffic_list_new_max = []
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        traffic_list_new_average = []
        traffic_list_new2_average = []
        for i in range(list_count_num):
            for j in range(list_num):
                traffic_in = traffic_count_list_average[i][j][0]
                traffic_out = traffic_count_list_average[i][j][1]
                if traffic_in is None and traffic_out is None:
                    traffic_list_new_average.append(float(0))
                elif traffic_in > traffic_out:
                    traffic_list_new_average.append(traffic_in)
                else:
                    traffic_list_new_average.append(traffic_out)
                traffic_dit = {i: traffic_list_new_average}

            traffic_list_new2_average.append(traffic_dit)
            traffic_list_new_average = []
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        #按顺序将每台主机的同一行的数据放到一个新的列表
        traffic_list_new3_max = []
        traffic_list_new4_max = []
        for i in range(list_num):
            for j in range(list_count_num):
                traffic_0 = traffic_list_new2_max[j][j][i]
                traffic_list_new3_max.append(traffic_0)
            traffic_dit2 = {i: traffic_list_new3_max}
            traffic_list_new3_max = []
            traffic_list_new4_max.append(traffic_dit2)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        traffic_list_new3_average = []
        traffic_list_new4_average = []
        for i in range(list_num):
            for j in range(list_count_num):
                traffic_0 = traffic_list_new2_average[j][j][i]
                traffic_list_new3_average.append(traffic_0)
            traffic_dit2 = {i: traffic_list_new3_average}
            traffic_list_new3_average = []
            traffic_list_new4_average.append(traffic_dit2)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        #将所有主机的同一条数据进行加运算后放到最终的列表中
        traffic_list_new5_max = []
        for i in range(list_num):
            traffic_1 = traffic_list_new4_max[i][i]
            traffic_1_sum = sum(traffic_1)
            traffic_list_new5_max.append(traffic_1_sum)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        traffic_list_new5_average = []
        for i in range(list_num):
            traffic_1 = traffic_list_new4_average[i][i]
            traffic_1_sum = sum(traffic_1)
            traffic_list_new5_average.append(traffic_1_sum)
    except Exception,e:
        Logger_Error_File.exception(e)

    try:
        #求流量的最大值
        traffic_max = round(max(traffic_list_new5_max) * 8 / float(1024) / float(1024), 2)
        #求流量的平均值
        traffic_new5_sum = sum(traffic_list_new5_average)
        traffic_new5_len = float(len(traffic_list_new5_average))
        traffic_average = round(traffic_new5_sum / traffic_new5_len * 8 / float(1024) / float(1024), 2)

        models.Operator_month_count.objects.create(operator=operator.encode('utf-8'), month=year_s + '/' + month_s,
                                                   max_value=traffic_max,
                                                   average_value=traffic_average, comment=area_s)
    except Exception,e:
        Logger_Error_File.exception(e)

    return HttpResponse('ok')

#存储区域月统计的流量数据_NEW
def handle_area_api_new(request,date,host,operator,compute,area):

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        if data == 0:
            continue
        elif data == 1:
            rrd = cur.fetchall()
        elif data == 2:
            rrd = cur.fetchall()

        cur.close()
        conn.close()

        for item in rrd:
            rrd_item = item.__str__()
            rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
                ')').strip(',').strip("'").encode('utf-8')
            if os.path.exists(rrd_file_path):
                rrd_file_list.append(rrd_file_path)
            else:
                continue

    # 通过rrdtool查询rrd数据
    fetch_result_list = []
    fetch_result_list_max = []
    fetch_result_list_average = []
    fetch_result_dict_max_count = {}
    fetch_result_dict_average_count = {}

    for item in rrd_file_list:
        start_time_stamp_rrd = str('-s' + ' ' + start_timestamp)
        end_time_stamp_rrd = str('-e' + ' ' + end_timestamp)
        fetch_result_max = rrdtool.fetch(item, str('MAX'), start_time_stamp_rrd, end_time_stamp_rrd)
        fetch_result_list_max.append(fetch_result_max)
        fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), start_time_stamp_rrd, end_time_stamp_rrd)
        fetch_result_list_average.append(fetch_result_average)
        fetch_result_dict_max = {item: fetch_result_max}
        fetch_result_dict_max_count.update(fetch_result_dict_max)
        fetch_result_dict_average = {item: fetch_result_average}
        fetch_result_dict_average_count.update(fetch_result_dict_average)

    # 将每个主机的流量添加到一个新的列表
    traffic_count_list_max = []
    for k, v in fetch_result_dict_max_count.items():
        traffic_count_list_max.append(v[2])
    traffic_count_list_average = []
    for k, v in fetch_result_dict_average_count.items():
        traffic_count_list_average.append(v[2])
    data_len_list = []
    for item in range(len(traffic_count_list_max)):
        data = len(traffic_count_list_max[item])
        data_len_list.append(data)
    def max_list(lt):
        temp = 0
        for i in lt:
            if lt.count(i) > temp:
                max_str = i
                temp = lt.count(i)
        return max_str
    if len(traffic_count_list_max) == 1:
        list_num = len(traffic_count_list_max[0])
    else:
        list_num = max_list(data_len_list)
    # 总共的列表个数
    list_count_num = len(traffic_count_list_max)

    # 将进出流量的大值放到新的列表中
    traffic_list_new_max = []
    traffic_list_new2_max = []
    for i in range(list_count_num):
        for j in range(list_num):
            traffic_in = traffic_count_list_max[i][j][0]
            traffic_out = traffic_count_list_max[i][j][1]
            if traffic_in is None and traffic_out is None:
                traffic_list_new_max.append(float(0))
            elif traffic_in > traffic_out:
                traffic_list_new_max.append(traffic_in)
            else:
                traffic_list_new_max.append(traffic_out)
            traffic_dit = {i: traffic_list_new_max}

        traffic_list_new2_max.append(traffic_dit)
        traffic_list_new_max = []

    traffic_list_new_average = []
    traffic_list_new2_average = []
    for i in range(list_count_num):
        for j in range(list_num):
            traffic_in = traffic_count_list_average[i][j][0]
            traffic_out = traffic_count_list_average[i][j][1]
            if traffic_in is None and traffic_out is None:
                traffic_list_new_average.append(float(0))
            elif traffic_in > traffic_out:
                traffic_list_new_average.append(traffic_in)
            else:
                traffic_list_new_average.append(traffic_out)
            traffic_dit = {i: traffic_list_new_average}

        traffic_list_new2_average.append(traffic_dit)
        traffic_list_new_average = []

    # 按顺序将每台主机的同一行的数据放到一个新的列表
    traffic_list_new3_max = []
    traffic_list_new4_max = []
    for i in range(list_num):
        for j in range(list_count_num):
            traffic_0 = traffic_list_new2_max[j][j][i]
            traffic_list_new3_max.append(traffic_0)
        traffic_dit2 = {i: traffic_list_new3_max}
        traffic_list_new3_max = []
        traffic_list_new4_max.append(traffic_dit2)

    traffic_list_new3_average = []
    traffic_list_new4_average = []
    for i in range(list_num):
        for j in range(list_count_num):
            traffic_0 = traffic_list_new2_average[j][j][i]
            traffic_list_new3_average.append(traffic_0)
        traffic_dit2 = {i: traffic_list_new3_average}
        traffic_list_new3_average = []
        traffic_list_new4_average.append(traffic_dit2)

    # 将所有主机的同一条数据进行加运算后放到最终的列表中
    traffic_list_new5_max = []
    for i in range(list_num):
        traffic_1 = traffic_list_new4_max[i][i]
        traffic_1_sum = sum(traffic_1)
        traffic_list_new5_max.append(traffic_1_sum)

    traffic_list_new5_average = []
    for i in range(list_num):
        traffic_1 = traffic_list_new4_average[i][i]
        traffic_1_sum = sum(traffic_1)
        traffic_list_new5_average.append(traffic_1_sum)

    # 求流量的最大值
    traffic_max = round(max(traffic_list_new5_max) * 8 / float(1024) / float(1024), 2)
    # 求流量的平均值
    traffic_new5_sum = sum(traffic_list_new5_average)
    traffic_new5_len = float(len(traffic_list_new5_average))
    traffic_average = round(traffic_new5_sum / traffic_new5_len * 8 / float(1024) / float(1024), 2)

    models.Area_month_count.objects.create(area=area_s,operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_max,average_value=traffic_average)

    return HttpResponse('ok')

#存储业务线统计的流量数据_NEW
def handle_service_line_api_new(request,date,host,operator,compute,area,service_line):

    start_time_h = "00:00:00"
    end_time_h = "23:59:59"
    da = [1,3,5,7,8,10,12]
    xiao = [4,6,9,11]
    month_s = str(date.split('-')[1:]).strip('[]').strip("u").strip("'").encode('utf-8')
    year_s = str(date.split('-')[:1]).strip('[]').strip("u").strip("'").encode('utf-8')
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

        conn = MySQLdb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, passwd=DB_PASSWORD, db=DB_DATABASE)
        cur = conn.cursor()

        sql = "select data_source_path from data_template_data where name_cache REGEXP 'Traffic' and name_cache REGEXP '{0}' and name_cache REGEXP '{1}'".format(
            item_str, operator_1)
        data = cur.execute(sql)
        if data == 0:
            continue
        elif data == 1:
            rrd = cur.fetchall()
        elif data == 2:
            rrd = cur.fetchall()

        cur.close()
        conn.close()

        for item in rrd:
            rrd_item = item.__str__()
            rrd_file_path = rrd_item.replace('<path_rra>', rrdpath).strip('(').strip(')').strip(',').strip("'").strip(
                ')').strip(',').strip("'").encode('utf-8')
            if os.path.exists(rrd_file_path):
                rrd_file_list.append(rrd_file_path)
            else:
                continue

    # 通过rrdtool查询rrd数据
    fetch_result_list = []
    fetch_result_list_max = []
    fetch_result_list_average = []
    fetch_result_dict_max_count = {}
    fetch_result_dict_average_count = {}

    for item in rrd_file_list:
        start_time_stamp_rrd = str('-s' + ' ' + start_timestamp)
        end_time_stamp_rrd = str('-e' + ' ' + end_timestamp)
        fetch_result_max = rrdtool.fetch(item, str('MAX'), start_time_stamp_rrd, end_time_stamp_rrd)
        fetch_result_list_max.append(fetch_result_max)
        fetch_result_average = rrdtool.fetch(item, str('AVERAGE'), start_time_stamp_rrd, end_time_stamp_rrd)
        fetch_result_list_average.append(fetch_result_average)
        fetch_result_dict_max = {item: fetch_result_max}
        fetch_result_dict_max_count.update(fetch_result_dict_max)
        fetch_result_dict_average = {item: fetch_result_average}
        fetch_result_dict_average_count.update(fetch_result_dict_average)

    # 将每个主机的流量添加到一个新的列表
    traffic_count_list_max = []
    for k, v in fetch_result_dict_max_count.items():
        traffic_count_list_max.append(v[2])
    traffic_count_list_average = []
    for k, v in fetch_result_dict_average_count.items():
        traffic_count_list_average.append(v[2])
    data_len_list = []
    for item in range(len(traffic_count_list_max)):
        data = len(traffic_count_list_max[item])
        data_len_list.append(data)

    def max_list(lt):
        temp = 0
        for i in lt:
            if lt.count(i) > temp:
                max_str = i
                temp = lt.count(i)
        return max_str

    if len(traffic_count_list_max) == 1:
        list_num = len(traffic_count_list_max[0])
    else:
        list_num = max_list(data_len_list)
    # 总共的列表个数
    list_count_num = len(traffic_count_list_max)
    # 将进出流量的大值放到新的列表中
    traffic_list_new_max = []
    traffic_list_new2_max = []
    for i in range(list_count_num):
        for j in range(list_num):
            traffic_in = traffic_count_list_max[i][j][0]
            traffic_out = traffic_count_list_max[i][j][1]
            if traffic_in is None and traffic_out is None:
                traffic_list_new_max.append(float(0))
            elif traffic_in > traffic_out:
                traffic_list_new_max.append(traffic_in)
            else:
                traffic_list_new_max.append(traffic_out)
            traffic_dit = {i: traffic_list_new_max}

        traffic_list_new2_max.append(traffic_dit)
        traffic_list_new_max = []

    traffic_list_new_average = []
    traffic_list_new2_average = []
    for i in range(list_count_num):
        for j in range(list_num):
            traffic_in = traffic_count_list_average[i][j][0]
            traffic_out = traffic_count_list_average[i][j][1]
            if traffic_in is None and traffic_out is None:
                traffic_list_new_average.append(float(0))
            elif traffic_in > traffic_out:
                traffic_list_new_average.append(traffic_in)
            else:
                traffic_list_new_average.append(traffic_out)
            traffic_dit = {i: traffic_list_new_average}

        traffic_list_new2_average.append(traffic_dit)
        traffic_list_new_average = []

    # 按顺序将每台主机的同一行的数据放到一个新的列表
    traffic_list_new3_max = []
    traffic_list_new4_max = []
    for i in range(list_num):
        for j in range(list_count_num):
            traffic_0 = traffic_list_new2_max[j][j][i]
            traffic_list_new3_max.append(traffic_0)
        traffic_dit2 = {i: traffic_list_new3_max}
        traffic_list_new3_max = []
        traffic_list_new4_max.append(traffic_dit2)

    traffic_list_new3_average = []
    traffic_list_new4_average = []
    for i in range(list_num):
        for j in range(list_count_num):
            traffic_0 = traffic_list_new2_average[j][j][i]
            traffic_list_new3_average.append(traffic_0)
        traffic_dit2 = {i: traffic_list_new3_average}
        traffic_list_new3_average = []
        traffic_list_new4_average.append(traffic_dit2)

    # 将所有主机的同一条数据进行加运算后放到最终的列表中
    traffic_list_new5_max = []
    for i in range(list_num):
        traffic_1 = traffic_list_new4_max[i][i]
        traffic_1_sum = sum(traffic_1)
        traffic_list_new5_max.append(traffic_1_sum)

    traffic_list_new5_average = []
    for i in range(list_num):
        traffic_1 = traffic_list_new4_average[i][i]
        traffic_1_sum = sum(traffic_1)
        traffic_list_new5_average.append(traffic_1_sum)

    # 求流量的最大值
    traffic_max = round(max(traffic_list_new5_max) * 8 / float(1024) / float(1024), 2)
    # 求流量的平均值
    traffic_new5_sum = sum(traffic_list_new5_average)
    traffic_new5_len = float(len(traffic_list_new5_average))
    traffic_average = round(traffic_new5_sum / traffic_new5_len * 8 / float(1024) / float(1024), 2)

    models.Service_line_month_count.objects.create(service_line=service_line_s,area=area_s,operator=operator.encode('utf-8'),month=year_s+'/'+month_s,max_value=traffic_max,average_value=traffic_average)

    return HttpResponse('ok')