# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Test(models.Model):

    Hostname = models.CharField(max_length=255)

    Password = models.CharField(max_length=255)

class Compute(models.Model):

    Compute = models.CharField(max_length=255)