
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^carts/$', views.CartsView.as_view()),


    # 11. 购物车 全选 carts/selection/
    url(r'^carts/selection/$', views.CartAllSelectView.as_view()),

    # 简单购物车展示 carts/simple/
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),



]
