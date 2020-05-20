import json
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views import View
import jwt
from rest_framework.generics import ListCreateAPIView

from apps.meiduo_admin.serializers.user import UserSerializer, UserAddSerializer
from apps.users.models import User
from apps.meiduo_admin.mixins import MeiduoPagination

# 1.用户信息展示
class UsersCountView(ListCreateAPIView):

    pagination_class = MeiduoPagination

    # page=1&pagesize=10&keyword=
    # page=1&pagesize=10&keyword=laowang
    # 自定义 返回的 查询数据--如果 是搜索的 一个; 如果不是 all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            # 一个
            return User.objects.filter(username__contains=keyword)
        else:
            # all()
            return User.objects.all()

    # 自定义 返回的  序列化器的类
    def get_serializer_class(self):

        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserAddSerializer





class LoginView(View):
    def post(self, request):
        # - 接收参数，
        json_dict = json.loads(request.body.decode())
        username = json_dict.get('username')
        password = json_dict.get('password')

        # - 校验参数，--校验正则 是否为空

        # - 登录认证
        user = authenticate(username=username, password=password)

        payload = {
            'id': user.id,
            'username': user.username,
            'exp': datetime.now() + timedelta(days=7)
        }
        # - 保持登录状态 生成 token
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')
        # 千万注意 token 类型是 bytes--->Str给前端
        # - 返回登录结果 {token:}
        return JsonResponse({
            'id': user.id,
            'username': username,
            'token': token.decode()
        })
