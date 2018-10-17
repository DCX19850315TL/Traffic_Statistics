# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,render_to_response
# Create your views here.
from django.http.response import HttpResponse
from statistics import models
import MySQLdb

def index(request):

    conn = MySQLdb.connect(host='10.160.92.65',port=3306,user='root',passwd='123456',db='cacti')
    cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    data = cur.execute('select * from statistics_test')
    all_data = cur.fetchall()

    cur.close()
    conn.close()

    return render_to_response('index.html',{'data':all_data})

