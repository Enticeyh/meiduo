from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

    # 热销排行 hot/(?P<category_id>\d+)/
    url(r'^hot/(?P<category_id>\d+)/$', views.HotView.as_view()),

    # 详情页 detail/(?P<sku_id>\d+)/
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),

    #  统计 分类的 访问量 detail/visit/(?P<category_id>\d+)/
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.GoodsVisitView.as_view()),



]
