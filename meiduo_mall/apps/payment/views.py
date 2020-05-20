import os

from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from alipay import AliPay

from apps.orders.models import OrderInfo
from apps.payment.models import Payment
from utils.response_code import RETCODE


class AliPaySuccessView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.解析参数 --queydict---dict
        data = request.GET.dict()

        # 2.剔除 sign 签名
        signature = data.pop('sign')

        # 加自己的校验 ---订单是否存在--- 金额是否一致

        # 3.支付宝校验 参数的 真伪
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,

            # 美多的 私钥路径
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/keys/app_private_key.pem'),
            # alipay的 公钥路径
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'keys/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        sucess = alipay.verify(data, signature)

        if sucess:
            Payment.objects.create(
                order_id=data.get('out_trade_no'),
                trade_id=data.get('trade_no')
            )

        # 4.如果校验通过 --存储 trade_no

        # 5.返回前端的数据
        return render(request, 'pay_success.html', {'trade_id': data.get('trade_no')})


class AliPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        # -  1.接收参数 order_id
        # - 2.校验order是否存在
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except:
            return render(request, '404.html')

        # - 3.导包 alipay

        # - 4.实例化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,

            # 美多的 私钥路径
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/keys/app_private_key.pem'),
            # alipay的 公钥路径
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                'keys/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # - 5.构建拼接 支付宝的支付网址  'https://openapi.alipaydev.com/gateway.do?' + "由支付宝加密之后的参数"
        order_string = alipay.api_alipay_trade_page_pay(
            subject="美多商城%s" % order_id,
            out_trade_no=order.order_id,
            total_amount=str(order.total_amount),
            return_url=settings.ALIPAY_RETURN_URL
        )
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
