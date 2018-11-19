# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Test(models.Model):

    Hostname = models.CharField(max_length=255)

    Password = models.CharField(max_length=255)

class Compute(models.Model):

    Compute = models.CharField(max_length=255)

class Step(models.Model):

    Step = models.CharField(max_length=255)

class Operator(models.Model):

    Operator = models.CharField(max_length=255)

class Service_line(models.Model):

    Service_line = models.CharField(max_length=255)

class Area(models.Model):

    Area = models.CharField(max_length=255)

class Operator_compute_result(models.Model):

    operator = models.CharField(max_length=255)
    start_time = models.CharField(max_length=255,default="00-00-00 00:00:00")
    end_time = models.CharField(max_length=255,default="00-00-00 00:00:00")
    max_value = models.FloatField(default=None,blank=True)
    average_value = models.FloatField(default=None,blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Area_compute_result(models.Model):

    area = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    start_time = models.CharField(max_length=255, default="00-00-00 00:00:00")
    end_time = models.CharField(max_length=255, default="00-00-00 00:00:00")
    max_value = models.FloatField(default=None, blank=True)
    average_value = models.FloatField(default=None, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Service_line_compute_result(models.Model):

    service_line = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    start_time = models.CharField(max_length=255, default="00-00-00 00:00:00")
    end_time = models.CharField(max_length=255, default="00-00-00 00:00:00")
    max_value = models.FloatField(default=None, blank=True)
    average_value = models.FloatField(default=None, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Operator_month_count(models.Model):

    operator = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    max_value = models.FloatField(default=None, blank=True)
    average_value = models.FloatField(default=None, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=255,default=None)

class Area_month_count(models.Model):

    area = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    max_value = models.FloatField(default=None, blank=True)
    average_value = models.FloatField(default=None, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Service_line_month_count(models.Model):

    service_line = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    max_value = models.FloatField(default=None, blank=True)
    average_value = models.FloatField(default=None, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

class Host_group(models.Model):

    group_name = models.CharField(max_length=255)
    comment = models.TextField()