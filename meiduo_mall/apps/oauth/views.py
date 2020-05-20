from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from utils.response_code import RETCODE


# 是否绑定 openid
def is_bind_openid(openid, request):
    # 1.去数据查询 有没有 这个 openid
    try:
        auth_user = OAuthQQUser.objects.get(openid=openid)
    except Exception as e:
        # 3.如果没有---绑定页面跳转
        from utils.secret import SecretOauth
        openid = SecretOauth().dumps({'openid':openid})
        return render(request, 'oauth_callback.html', context={'openid': openid})
    else:

        # 2.如果有 ---跳首页
        user = auth_user.user
        # 保持登录状态
        login(request, user)

        # 设置cookie
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=24 * 30 * 3600)
        return response


class QQOauthCallbackView(View):
    def get(self, request):
        # http://www.meiduo.site:8000/oauth_callback
        #           ?code=5E6553674D903E118B59720C126C4B4D&state=None

        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('code无效了!')

        # 1.实例化 QQ 认证对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=None)
        # 1.code -- token
        token = oauth.get_access_token(code)

        # 2.token--openid
        openid = oauth.get_open_id(token)

        # 判断是否绑定 openid
        response = is_bind_openid(openid, request)

        return response

    def post(self, request):

        # 1.解析参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        if openid is None:
            return http.HttpResponseForbidden('openid失效了')
        # 解密
        from utils.secret import SecretOauth
        openid = SecretOauth().loads(openid).get('openid')

        # 2.校验 判空--正则--图片--短信验证码

        # 3.校验mobile 是否存在
        try:
            user = User.objects.get(mobile=mobile)
            # 如果密码不正确
            if not user.check_password(pwd):
                return render(request,'oauth_callback.html',{'errmsg':'用户或密码不正确'})
        except Exception as e:
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)

        # 4. 绑定openid
        oauth_user = OAuthQQUser.objects.create(user=user, openid=openid)

        # 5.保持状态--set_cookie--重定向首页--
        login(request, oauth_user.user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=24 * 30 * 3600)
        return response


class QQAuthURLView(View):
    # 1.获取qq登录网址
    def get(self, request):


        # 1.实例化 QQ 认证对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=None)

        # 2.获取 login
        login_url = oauth.get_qq_url()

        # 3.返回
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
