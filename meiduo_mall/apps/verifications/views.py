import random
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.verifications import constants


# 2.短信验证码
class SmsCodeView(View):
    def get(self, request, mobile):
        # - 1.接收参数 解析参数---路径参数mobile, 查询参数request.GET
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # - 2.校验前端图片验证码和redis里面的 是否正确
        redis_client = get_redis_connection('verify_image_code')
        redis_img_code = redis_client.get('img_%s' % uuid)

        # 如果redis 是空的
        if redis_img_code is None:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})

        # 图片验证码 一次 就失效了, 删除
        redis_client.delete('img_%s' % uuid)

        # 校验 对比 千万注意: redis获取出来的数据类型 是 Bytes -- decode()
        if image_code.lower() != redis_img_code.decode().lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码验证失败!'})

        # - 3.生成随机6位码---random.randint()--存储redis数据库 mobile:6位码
        sms_code = random.randint(100000, 999999)
        sms_code_client = get_redis_connection('sms_code')

        # 1.取出 redis 存储 标识
        send_flag = sms_code_client.get('send_flag_%s' % mobile)
        # 2.判断标识 是否存在 --不存在 --发短信
        if send_flag:
            # 3.存在 --返回 提示 不发送
            return http.HttpResponseForbidden('短信发送太频繁')

        # 1.实例化 管道
        pipeline = sms_code_client.pipeline()

        # 2.将任务 添加到管道
        pipeline.setex('send_flag_%s' % mobile, 60, 1)

        pipeline.setex("sms_%s" % mobile, 300, sms_code)

        # 3.执行管道
        pipeline.execute()

        print('短信验证码:', sms_code)

        # - 4.使用第三方 容联云 发短信
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)

        # - 5.返回响应对象
        return http.JsonResponse({'code': 0, 'errmsg': '短信发送成功!'})


# 1.图片 验证码
class ImageCodeView(View):
    def get(self, request, uuid):
        # 1. 前端发请求 -要图形--UUID
        # 2. 解析参数UUID --正则校验

        # 3. 生成图片验证码:str:bytes--str
        from libs.captcha.captcha import captcha
        img_code, image = captcha.generate_captcha()

        # 4. image_code === redis数据库
        from django_redis import get_redis_connection
        # 4.2 链接 客户端
        client = get_redis_connection('verify_image_code')

        # 4.3 存储 img_code
        client.setex('img_%s' % uuid, 300, img_code)
        # client.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 5. 返回前端 图片验证码---content_type = "image/jpg"
        return http.HttpResponse(image, content_type='image/jpg')

