
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),

    # 提交订单 数据 orders/commit/
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),

    # 提交成功 页面 展示 orders/success/
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),


]
