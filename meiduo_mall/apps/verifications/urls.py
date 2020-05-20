
from django.conf.urls import url

from . import views

urlpatterns = [
    # 1图形 验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    # 2.短信验证码
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SmsCodeView.as_view()),

]
