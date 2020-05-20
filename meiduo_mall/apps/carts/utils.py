import json

from django_redis import get_redis_connection

from utils.cookiesecret import CookieSecret


def merge_cart_cookie_to_redis(request, response):
    # 1.获取 cookie 所有数据
    cookie_str = request.COOKIES.get('carts')

    # 2.如果有值--解密
    if cookie_str:
        cookie_cart_dict = CookieSecret.loads(cookie_str)
        # 3.链接redis数据库
        client = get_redis_connection('carts')

        # 4.遍历数据 -- 覆盖 redis的值 {'sku_id':{count:}}
        for sku_id, sku_value in cookie_cart_dict.items():
            client.hset(request.user.id, sku_id, json.dumps(sku_value))

    # 5.删除cookie的 购物车数据
    response.delete_cookie('carts')
