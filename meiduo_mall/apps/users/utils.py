# 1.导包
import re

from django.conf import settings
from django.contrib.auth.backends import ModelBackend


# 3.生成 激活链接
def generate_verify_email_url(user):
    # http://www.meiduo.site:8000/emails/verification/
    #   ?token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTU2NjE5ODk4MywiZXhwIjoxNTY2MjAyNTgzfQ.eyJ1c2VyX2lkIjo2LCJlbWFpbCI6ImxpdWNoZW5nZmVuZzY2NjZAMTYzLmNvbSJ9.okIKKAHjeskFild3EZeK3034N2r0vMb_tvUaVA7h4qPdfxmsDG4JvzXsTLl2_98Ln6rpWN4EmAdrdthZeG2DdQ

    # 1.获取 比传的 两个 参数 user_id email
    data_dict = {'user_id': user.id, 'email': user.email}
    # 2.加密 数据
    from utils.secret import SecretOauth
    dumps_str = SecretOauth().dumps(data_dict)

    # 3. 拼接完整的 带参数 的链接
    return settings.EMAIL_ACTIVE_URL + '?token=' + dumps_str


# 2.类继承
from apps.users.models import User

from meiduo_mall.settings.dev import logger


# 封装 校验 账号 的函数 ---支持 username 也支持 mobile
def get_user_by_account(account, request):
    #  判断 是否 是后台用户---request is None
    if request is None:
        try:
            user = User.objects.get(username=account, is_staff=True)
        except Exception as e:
            logger.error(e)
            return None
        else:
            return user

    else:
        # 前台用户
        try:
            if re.match(r'^1[345789]\d{9}$', account):

                user = User.objects.get(mobile=account)
            else:
                user = User.objects.get(username=account)
        except Exception as e:
            logger.error(e)
            return None
        else:
            return user


class UsernameMobileAuthBackend(ModelBackend):
    # 3.重写authenticate
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.校验 账号
        user = get_user_by_account(username, request)

        # 2.校验密码是否正确 check_password()
        if user and user.check_password(password):
            # 3.返回 user 对象
            return user

            # 4.dev 配置
