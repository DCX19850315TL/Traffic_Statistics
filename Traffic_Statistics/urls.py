"""Traffic_Statistics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from statistics.views import index,handle,show_operator,show_compute,show_area,show_service_line
from statistics.views import handle_api
from get_data_display.views import get_operator_data,get_operator_month_count
from get_data_display.views import get_operator_api_data

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/',index),
    url(r'^handle/',handle),
    url(r'^show_operator/',show_operator),
    url(r'^show_compute/',show_compute),
    url(r'^show_area/',show_area),
    url(r'^show_service_line/',show_service_line),
    url(r'^handle_api/date(.+)host(.+)operator(\w+)compute(\w+)area(\w+)/$',handle_api),
    url(r'^get_operator_data/',get_operator_data),
    url(r'^get_operator_api_data/',get_operator_api_data),
    url(r'^get_operator_month_count/',get_operator_month_count),
]
