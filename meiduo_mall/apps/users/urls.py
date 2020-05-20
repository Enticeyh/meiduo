from django.conf.urls import url

from . import views

urlpatterns = [

    # 1.注册
    url(r'^register/$', views.RegisterView.as_view()),

    # 2.用户名 重复 判断
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),

    # 3.手机号 重复 判断  mobiles/(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # 4.账号登录 login
    url(r'^login/$', views.LoginView.as_view(), name='login'),

    # 5.退出  logout/
    url(r'^logout/$', views.LogOutView.as_view(), name='logout'),

    # 4.用户中心     info
    url(r'^info/$', views.InfoView.as_view(), name='info'),

    # 5.用户中心--新增邮箱     emails
    url(r'^emails/$', views.EmailView.as_view()),

    # 6.用户中心--激活邮箱
    url(r'^emails/verification/$', views.EmailVerifyView.as_view()),

    # 7.收货地址
    url(r'^address/$', views.AddressView.as_view()),

    # 8.新增 收货地址 addresses/create/
    url(r'^addresses/create/$', views.AddressCreateView.as_view()),

    # 9. 修改密码
    url(r'^password/$', views.ChangePwdView.as_view(), name='password'),

    # 10.用户浏览记录 browse_histories/
    url(r'^browse_histories/$', views.HistoriesView.as_view()),





]
