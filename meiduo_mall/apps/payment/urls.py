
from django.conf.urls import url

from . import views

urlpatterns = [

    # 1.获取 支付宝的  支付网址 url
    url(r'^payment/(?P<order_id>\d+)/$', views.AliPayView.as_view()),


    # 2.获取 支付宝的 支付凭证
    url(r'^payment/status/$', views.AliPaySuccessView.as_view()),

]
