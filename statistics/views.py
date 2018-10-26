# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response
# Create your views here.
from django.http.response import HttpResponse
from statistics import models
import MySQLdb
import json

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

        host = request.POST.get('host_data_out')
        host_str = host.encode('utf-8')
        operator = request.POST.get('operator_data')
        operator_str = operator.encode('utf-8')
        conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = 'select operator from statistics_operator where id = %s'
        params = operator_str
        data = cur.execute(sql,params)
        operator_type = cur.fetchall()

        cur.close()
        conn.close()

        operator_type_str = str(operator_type[0]).strip(')').strip('(').strip(',').strip("'").encode('utf-8')
        operator_type_str1 = "- operator_type_str"

        conn = MySQLdb.connect(host='10.160.92.77', port=3306, user='root', passwd='123456', db='cacti')
        cur = conn.cursor()

        sql = 'select data_source_path from data_template_data where name_cache REGEXP "Traffic" and name_cache REGEXP %s'
        data = cur.execute(sql,operator_type_str)
        rrd = cur.fetchall()

        cur.close()
        conn.close()

        print rrd

    return HttpResponse('aaa')

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