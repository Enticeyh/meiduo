import json

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import re
from django_redis import get_redis_connection
from django.contrib.auth import logout

from apps.goods.models import SKU
from apps.users.utils import generate_verify_email_url
from meiduo_mall.settings.dev import logger
from apps.users.models import User, Address
from utils.response_code import RETCODE
from utils.secret import SecretOauth


# 10.用户浏览记录
class HistoriesView(LoginRequiredMixin, View):
    def post(self, request):

        # 1.接收参数
        sku_id = json.loads(request.body.decode()).get('sku_id')


        # 2.校验参数 -- sku存不存在
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return render(request, '404.html')

        # sku_id 前端参数
        # sku.id 从数据库读取出来的id --- 建议使用第二种

        # 3.链接redis的客户端
        client = get_redis_connection('history')
        save_key = 'history_%s' % request.user.id
        pipeline = client.pipeline()

        # 3.1先去重
        pipeline.lrem(save_key, 0, sku.id)
        # 3.2再存储
        pipeline.lpush(save_key, sku.id)
        # 3.3截取5个数据
        pipeline.ltrim(save_key, 0, 4)

        pipeline.execute()

        # 4.返回响应对象
        return http.JsonResponse({'code': 0, 'errmsg': "存储成功!"})

    def get(self, request):

        # 1.链接redis数据 库  查询 所有的 sku_id
        client = get_redis_connection('history')
        save_key = 'history_%s' % request.user.id
        sku_ids = client.lrange(save_key, 0, -1)

        print('SKU:{}'.format(sku_ids))

        # 通过 范围查询 获取 所有 符合条件的 sku--- 结果是没问题--但是顺序混乱了

        # skus = SKU.objects.filter(id__in=sku_ids)
        # sku_list = []
        # for sku in skus:
        #
        #     sku_list.append({
        #         'id': sku.id,
        #         'name': sku.name,
        #         'default_image_url': sku.default_image.url,
        #         'price': sku.price
        #
        #     })

        # 2.根据 sku_id 获取 对应的 sku对象
        sku_list = []
        for sku_id in sku_ids:
            try:
                sku = SKU.objects.get(pk=sku_id)
                sku_list.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price
                })
            except Exception as e:
                print(e)

        # 3.装换前端 需要的数据格式

        # 4.返回 JsonResponse
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': sku_list})


# 9.修改密码
class ChangePwdView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):
        # 1.接收参数
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        new_cpwd = request.POST.get('new_cpwd')

        # 2.form json 判空 判正则
        #
        # 3.判断 两次密码 是否 一致
        if new_pwd != new_cpwd:
            return http.HttpResponseForbidden('两次密码不一致!')

        # 4.校验 原始密码是否正确-- check_passord()
        if not request.user.check_password(old_pwd):
            return http.HttpResponseForbidden('密码不正确!')

        # 5.修改 user.password值 --set_password()
        request.user.set_password(new_pwd)
        request.user.save()

        # 6.重定向到登录页
        return redirect(reverse("users:login"))


# 8.新增 收货地址
class AddressCreateView(LoginRequiredMixin, View):
    def post(self, request):

        # 判断当前用户 --增加的收货地址的个数 不能大于20
        # 第一种写法 : 站在 Address表的角度查数据
        count = Address.objects.filter(user=request.user, is_deleted=False).count()

        # 第二种写法 : 站在 User表的角度 查数据 1:n
        count = request.user.addresses.filter(is_deleted=False).count()
        print(count)

        if count > 20:
            return http.JsonResponse({'code': 0, 'errmsg': "收货地址最多20个"})

        # 1.接收参数 ---json--request.body
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.校验参数--判空--判正则--

        # 3.新增 数据库数据--Address.objects.create()
        try:
            address = Address.objects.create(
                user_id=request.user.id,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 0, 'errmsg': '增加失败!'})

        # 如果当前用户 没有收货地址, 赋值一个 地址 作为默认地址
        if request.user.default_address is None:
            request.user.default_address = address
            request.user.save()

        # 4.构建前端 需要的数据格式 {}
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 5.返回响应
        # return http.JsonResponse({'code': 0, 'errmsg': '增加成功!', "address": address_dict})
        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 7. 收货地址页面
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        # 1.查询当前用户的所有没删除的地址
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 2.构建前端数据格式  [{}]
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        context = {
            'default_address_id': user.default_address_id,
            'addresses': address_list,
        }
        return render(request, 'user_center_site.html', context=context)


class EmailVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接收token- 查询参数--request.GET
        token = request.GET.get('token')

        if not token:
            return http.HttpResponseForbidden('token无效了!')
        # 2.解密
        token_dict = SecretOauth().loads(token)

        # 3.校验 user_id  email
        try:
            user = User.objects.get(id=token_dict['user_id'], email=token_dict['email'])
            # 4.激活 email_active = True
            user.email_active = True
            user.save()
        except Exception as e:
            return http.HttpResponseForbidden('token有误!')

        # 5.重定向到 用户中心页面
        return redirect(reverse('users:info'))


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        # 1.接收参数 email json
        email = json.loads(request.body.decode()).get('email')

        # 2.修改 用户 的 emailshuxi属性
        request.user.email = email
        request.user.save()

        # 保存邮箱成功之后  发送邮件--网易发送---耗时任务--celery
        # 获取激活链接
        verify_url = generate_verify_email_url(request.user)
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)

        # 3.返回结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 用户中心显示
class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        # 1.render() --->jinja2渲染-- 前后端不分离
        # 2.JsonResponse--vue渲染---前后端分离

        # 3. render() ------- --->jinja2渲染--js变量---------- vue渲染
        return render(request, 'user_center_info.html', context)


# 5.退出
class LogOutView(View):
    def get(self, request):
        # 1.清空session==request.session.flush()
        # django==logout()
        logout(request)

        # 2.清空 cookie
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        return response


# 4.登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 1.接收解析参数-请求体form--request.POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验-判空--正则

        # 3.校验用户名和密码是否正确--User.objects.get(username=username,password=password)
        # django自带的登录函数--authenticate==>如果成功返回user对象, 如果失败None
        from django.contrib.auth import authenticate, login
        user = authenticate(request=request,username=username, password=password)

        # 登录失败
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误!'})

        # 4.保持登录状态
        login(request, user)

        # 是否 记住登录--本质 session过期时间
        if remembered == 'on':
            # 记住登录 None 14天
            request.session.set_expiry(None)
        else:
            # 不记住登录
            request.session.set_expiry(0)

        # 设置cookie --username--方便其他前端页面去cookie取值
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # response.set_cookie('username', username, max_age=24 * 3600 * 15)
        response.set_cookie('username', user.username, max_age=24 * 3600 * 15)

        # 合并购物车
        from apps.carts.utils import merge_cart_cookie_to_redis
        merge_cart_cookie_to_redis(request, response)

        # 5.重定向到首页
        return response

    """
    cookie:  macbook  1  3台
            iphone    16 1
            
    redis   macbook  1  1台
            iphone    4  1
            
            
    合并之后的: macbook  3台
              iphone   1
              iphone   1
    """


# 3.判断手机号是否重复
class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({'code': 0, 'errmsg': '手机号重复!', 'count': count})


# 2.判断用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        # - 1.接收前端参数 username
        # - 2.校验参数 username  User.objects.filter(username=username)
        # - 3.取个数 count()
        count = User.objects.filter(username=username).count()

        # - 4.返回前端响应个数
        # return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
        return http.JsonResponse({'code': 0, 'errmsg': '用户名重复!', 'count': count})


# 1.注册页面显示
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接收前端的请求
        # 2.解析参数s reqeust.POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')

        # 是否勾选
        allow = request.POST.get('allow')

        # 3.校验参数--判空,正则re, ajax判断是否重复
        # 判空
        # if not all([username, password, mobile]):
        #     return http.HttpResponseForbidden('参数不齐!')
        #
        # # 判断用户名正则
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
        #     return http.HttpResponseForbidden('请输入5-20个字符的用户')
        # # 判断密码正则
        # if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
        #     return http.HttpResponseForbidden('请输入8-20位的密码')
        # # 判断 密码是否一致
        # if password != password2:
        #     return http.HttpResponseForbidden('密码不一致')
        # # 判断手机号正则
        # if not re.match(r'^1[345789]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('手机号格式有误!')
        # # 是否勾选
        # if allow != 'on':
        #     return http.HttpResponseForbidden('请勾选!')
        #
        # # 完善补充 校验 短信验证码
        # # 1.接收 前端 用户 输入 短信验证码
        # msg_code = request.POST.get('msg_code')
        #
        # # 2.从redis取出后台 短信验证码
        # redis_client = get_redis_connection('sms_code')
        # redis_sms_code = redis_client.get("sms_%s" % mobile)
        # # 3.判断是否为空 后台 短信验证码
        # if redis_sms_code is None:
        #     return render(request, 'register.html', {'register_errmsg': '短信失效了'})
        #
        # # 4.判断 是否 和 前端 一致
        # if msg_code != redis_sms_code.decode():
        #     return render(request, 'register.html', {'register_errmsg': '短信验证码有误!'})

        # 4.注册用户-
        # -User.objects.create(username=username,password=password,mobile=mobile) 密码没加密
        # django-User--create_user(username=username,password=password,mobile=mobile) 密码加密
        try:
            from apps.users.models import User
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败 用户名或密码错误!'})

        # 5.保持登录状态--session--request.session[k]=v
        from django.contrib.auth import login
        login(request, user)

        # 6.返回响应对象--重定向到首页
        return redirect(reverse('contents:index'))
