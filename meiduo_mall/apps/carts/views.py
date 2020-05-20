import json

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.cookiesecret import CookieSecret


# 将重复的功能 抽取函数
def get_response(sku, count, selected):
    # 前端要的数据格式
    cart_sku = {
        'id': sku.id,
        'name': sku.name,
        'default_image_url': sku.default_image.url,
        'price': sku.price,

        'count': count,
        'selected': selected,
        'amount': sku.price * count
    }

    # 返回响应对象
    return http.JsonResponse({'code': 0, 'errmsg': '修改成功!', 'cart_sku': cart_sku})


class CartsSimpleView(View):
    def get(self, request):

        user = request.user

        if user.is_authenticated:
            # redis
            client = get_redis_connection('carts')
            redis_carts = client.hgetall(user.id)
            # 字典推导式
            cart_dict = {}
            for k, v in redis_carts.items():
                sku_id = int(k.decode())
                sku_dict = json.loads(v.decode())
                cart_dict[sku_id] = sku_dict
        else:
            # cookie
            cookie_str = request.COOKIES.get('carts')

            if cookie_str:
                cart_dict = CookieSecret.loads(cookie_str)
            else:
                cart_dict = {}


        # 根据sku_id 查询 sku 的数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        for sku_id in sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        # 返回结果
        return http.JsonResponse({'code': 0, 'errmsg': '查询成功!', 'cart_skus': cart_skus})


class CartAllSelectView(View):
    def put(self, request):
        # 1.接收参数
        selected = json.loads(request.body.decode()).get('selected', True)

        # 2.校验参数 -省略

        # 3.判断是否登录
        user = request.user
        dumps_str = ""
        if user.is_authenticated:
            # redis
            # 1.链接
            client = get_redis_connection('carts')

            # 2.取所有 hgetall == {b'5':b'{count:3,selected:true}'}
            redis_carts = client.hgetall(user.id)

            # 3.遍历所有 购物车数据 --修改 selected 属性 hset
            p1 = client.pipeline()

            for k, v in redis_carts.items():
                sku_id = int(k.decode())
                sku_dict = json.loads(v.decode())
                # 修改 所有购物车商品选中属性
                sku_dict['selected'] = selected

                p1.hset(user.id, sku_id, json.dumps(sku_dict))

            p1.execute()


        else:
            # cookie
            # 1.取出购物车的数据
            cookie_str = request.COOKIES.get('carts')

            # 2.如果有--解密
            if cookie_str:
                cart_dict = CookieSecret.loads(cookie_str)

                # 3.遍历字典--判断是否有---修改 selected
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                # 4.加密--set_cookie
                dumps_str = CookieSecret.dumps(cart_dict)
        response = http.JsonResponse({'code': 0, 'errmsg': "修改成功!"})

        if not user.is_authenticated:
            response.set_cookie('carts', dumps_str, max_age=24 * 3600 * 30)
        # 4.返回响应对象
        return response


class CartsView(View):
    # 1.购物车增加
    def post(self, request):
        # - 1.接收前端传递的参数 sku_id count selected --- json传参
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # - 2.校验参数 sku,count 是 init,  selected boolean
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return render(request, '404.html')

        try:
            count = int(count)
        except:
            return http.HttpResponseForbidden('count 类型必须是数字')

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('selected 类型必须是布尔类型')

        # - 3.判断是否登录 user.is_authenticated
        user = request.user
        response = http.JsonResponse({'code': 0, 'errmsg': '购物车添加成功'})
        if user.is_authenticated:
            # - 1.链接数据库 redis
            client = get_redis_connection('carts')

            # - 2.获取当前用户 所有 购物车数据  --hgetall ==> dict
            redis_carts = client.hgetall(user.id)

            # - 3.判断 当前 sku商品 在不在购物车
            # {b'5':b'{count:1,selected:true}'}
            if str(sku_id).encode() in redis_carts:

                # - 如果在 :  count += count---hset
                # 取出 dict中 b'{count:1,selected:true}'
                bytes_dict = redis_carts[str(sku_id).encode()]
                # 将 bytes==>str
                json_str = bytes_dict.decode()
                # 将 str ==> dict
                sku_dict = json.loads(json_str)

                sku_dict['count'] += count
                client.hset(user.id, sku_id, json.dumps(sku_dict))

            else:
                #     不存在: 新添加数据 hset
                new_sku = {'count': count, 'selected': selected}
                client.hset(user.id, sku_id, json.dumps(new_sku))

        else:
            print('未登录状态')
            # - 1.从cookie取出 购物车的数据--request.COOKIES
            carts_str = request.COOKIES.get('carts')

            # - 2.判断 如果有值 --- 解码--解密
            if carts_str:
                cart_dict = CookieSecret.loads(carts_str)
            else:
                cart_dict = {}

            # - 3.判断 商品 sku_id 在购物车 --将 老的购买个数 和 新的购买个数 sum求和
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count = origin_count + count

            # - 4.无论是否有 购物车的 商品--都赋值
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            #   5. 加密--cookie
            dumps_str = CookieSecret.dumps(cart_dict)
            response.set_cookie('carts', dumps_str, max_age=24 * 3600 * 30)

        return response

    # 2.购物车 查询
    def get(self, request):

        user = request.user

        # 1.判断是否登录
        if user.is_authenticated:
            # redis

            # 1.链接数据库
            client = get_redis_connection('carts')

            # 2.取所有 当期那user--hgetall==>dict
            redis_carts = client.hgetall(user.id)

            # 3.将 redis取出 bytes的字典--- 普通的字典
            # {b'5':b'{count:1,selected:2}'}
            cart_dict = {}
            for k, v in redis_carts.items():
                sku_id = int(k.decode())
                sku_dict = json.loads(v.decode())
                cart_dict[sku_id] = sku_dict

            # 字典推导式
            # cart_dict = {int(k.decode()): json.loads(v.decode()) for k, v in redis_carts.items()}


        else:
            # cookie
            cookie_str = request.COOKIES.get('carts')

            if cookie_str:
                # 解密
                cart_dict = CookieSecret.loads(cookie_str)
            else:
                cart_dict = {}

        # 根据购物车 sku_ids 获取--sku信息
        sku_ids = cart_dict.keys()

        # 构建前端 需要的数据格式
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(pk=sku_id)

            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),

                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))

            })

        context = {
            'cart_skus': sku_list
        }
        print(sku_list)
        return render(request, 'cart.html', context)

    # 3.购物车 修改
    def put(self, request):

        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 2.校验--省略
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return render(request, '404.html')

        # 3.判断是否登录
        user = request.user
        dumps_str = ""
        if user.is_authenticated:
            # redis
            client = get_redis_connection('carts')
            new_sku = {'count': count, 'selected': selected}
            client.hset(user.id, sku_id, json.dumps(new_sku))

        else:
            # cookie
            # 1.获取 所有购物车 数据 cookie
            cookie_str = request.COOKIES.get('carts')
            # 2.判断是否有 --有--解密
            if cookie_str:
                cart_dict = CookieSecret.loads(cookie_str)
            else:
                cart_dict = {}

            # 3. 整体覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 4.加密
            dumps_str = CookieSecret.dumps(cart_dict)

        response = get_response(sku, count, selected)
        if not user.is_authenticated:
            response.set_cookie('carts', dumps_str, max_age=24 * 3600 * 30)
        return response

    # 4.购物车  删除
    def delete(self, request):

        # 1.接收 sku_id
        sku_id = json.loads(request.body.decode()).get('sku_id')

        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return render(request, '404.html')

        # 2.判断是否登录
        user = request.user
        dumps_str = ""
        if user.is_authenticated:
            # redis
            # 1.链接数据库
            client = get_redis_connection('carts')

            # 2.删除
            client.hdel(user.id, sku_id)
        else:
            # cookie
            cookie_str = request.COOKIES.get('carts')

            if cookie_str:
                cart_dict = CookieSecret.loads(cookie_str)

                # 判断 sku_id  在在不在 购物车
                if sku_id in cart_dict:
                    del cart_dict[sku_id]

                    # 加密
                    dumps_str = CookieSecret.dumps(cart_dict)

        response = http.JsonResponse({'code': 0, 'errmsg': '删除成功!'})
        if not user.is_authenticated:
            response.set_cookie('carts', dumps_str, max_age=24 * 3600 * 30)
        # 返回JSon
        return response
