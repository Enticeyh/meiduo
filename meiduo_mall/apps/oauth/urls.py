
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^qq/login/$', views.QQAuthURLView.as_view()),

    # 2.QQ登录成功之后 ---回调 地址  oauth_callback/
    url(r'^oauth_callback/$', views.QQOauthCallbackView.as_view()),


]
