import json
from datetime import datetime
import time
from decimal import Decimal
from pprint import pprint

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE


class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        # 接收参数
        order_id = request.GET.get('order_id')

        # 校验订单
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except:
            return http.HttpResponseNotFound('订单不存在!')

        context = {
            'order_id': order.order_id,
            'payment_amount': order.total_amount,
            'pay_method': order.pay_method
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    def post(self, request):
        # 1.接收非表单 参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 2.校验参数
        try:
            address = Address.objects.get(pk=address_id)
        except:
            return http.HttpResponseNotFound('地址不存在!')

        # 校验支付方式 : 1.支付宝 alipay 2.货到付款 cash
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('美多商城暂不支持{}支付方式'.format(pay_method))

        # 3. 新增 OrderInfo 添加数据
        user = request.user
        #         年月日 时分秒 + 9个0 + user.id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ("%09d" % user.id)
        # 添加 局部 事务
        from django.db import transaction
        with transaction.atomic():

            # 设置 事务开始点-- 保存点
            sid = transaction.savepoint()

            try:
                order = OrderInfo.objects.create(order_id=order_id, user=user, address_id=address.id,
                                                 freight=Decimal('10.00'), pay_method=pay_method,
                                                 status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'], total_count=0,
                                                 total_amount=Decimal('0.00'))

                # 4. 新增 OrderGoods 添加数据--
                # - 已经选中的商品SKU---redis
                client = get_redis_connection('carts')
                redis_carts = client.hgetall(user.id)
                selected_dict = {}
                for k, v in redis_carts.items():
                    sku_id = int(k.decode())
                    sku_dict = json.loads(v.decode())

                    # 选中的商品 True
                    if sku_dict['selected']:
                        selected_dict[sku_id] = sku_dict

                for sku_id in selected_dict.keys():

                    while True:
                        # 当前购买的 sku的 所有信息--时时信息
                        sku = SKU.objects.get(pk=sku_id)

                        # 获取老库存 和 老销量
                        origin_stock = sku.stock
                        origin_sale = sku.sales

                        cart_count = selected_dict.get(sku_id).get('count')
                        # 判断库存 ;  购买个数 大于> sku的库存stock
                        if cart_count > sku.stock:
                            # 事务回滚
                            transaction.savepoint_rollback(sid)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '{}-库存不足!'.format(sku.name)})

                        # 加延迟 10s中---测试 并发下单
                        # time.sleep(10)

                        # sku 库存减少 销量增加
                        # sku.stock -= cart_count
                        # sku.sales += cart_count
                        # sku.save()

                        # 计算 将来修改的 库存 和销量只 ---加锁
                        new_stock = origin_stock - cart_count
                        new_sales = origin_sale + cart_count
                        result=SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock, sales=new_sales)


                        # 如果 库存非常充足, 只是 在下单的时候  老库存修改了, 应该是 能够下单成功的---内部自动继续下单
                        if result == 0:
                            continue

                        # spu  销量增加
                        sku.spu.sales += cart_count
                        sku.spu.save()

                        # 订单商品表的 必传字段 填写全了
                        OrderGoods.objects.create(order=order,sku=sku,
                            count=cart_count,
                            price=sku.price
                        )

                        # 计算 总计金额 总个数
                        order.total_count += cart_count
                        order.total_amount += sku.price * cart_count

                        # 下单成功--跳出循环
                        break

                # 最后 总的 支付金额 == 累加金额 +  运费
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                logger.error(e)

                # 事务回滚
                transaction.savepoint_rollback(sid)
                # 返回响应对象
                return http.JsonResponse({'code': 0, 'errmsg': '下单失败了'})

            # 事务提交
            transaction.savepoint_commit(sid)

        # 清空redis数据库 中选中的商品
        client.hdel(user.id, *selected_dict)

        # 返回响应对象
        return http.JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        # 1.获取 当前用户的 地址
        # 1.站在 地址表的 角度
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 2.站在 用户的  角度 -- 1:n
        addresses = user.addresses.filter(is_deleted=False)

        # 2.查询 redis 数据库 购物车数据--条件 选中的商品
        # {count:1, selected:true}
        client = get_redis_connection('carts')
        redis_carts = client.hgetall(user.id)

        # 条件 选中的商品
        # redis_carts = {b'1':b'{count:2,selected:true}'}
        selected_dict = {}
        for k, v in redis_carts.items():
            sku_id = int(k.decode())
            sku_dict = json.loads(v.decode())

            # 选中的商品 True
            if sku_dict['selected']:
                selected_dict[sku_id] = sku_dict

        # 3.根据 sku_ids 获取 sku商品数据
        total_amount = Decimal('0.00')
        total_count = 0
        freight = Decimal('10.00')

        sku_list = []
        for sku_id in selected_dict.keys():
            sku = SKU.objects.get(pk=sku_id)

            # 没有 count  和  amount 小计 的属性 --动态添加
            sku.count = selected_dict.get(sku_id).get('count')
            sku.amount = sku.count * sku.price

            # 修改过的 sku的集合list
            sku_list.append(sku)

            # 总金额 总个数
            total_amount += sku.amount
            total_count += sku.count

        # 总支付金额== 总金额  +  运费
        pay_amount = total_amount + freight

        context = {
            'addresses': addresses,
            'skus': sku_list,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': pay_amount,
            # 默认地址
            'default_address_id': user.default_address_id

        }

        return render(request, 'place_order.html', context)
