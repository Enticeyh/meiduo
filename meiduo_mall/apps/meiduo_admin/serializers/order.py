from rest_framework import serializers

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods

"""
  {
        "user": "zxc000",     
        "skus": [
            {
                "count": 1,
                "price": "6499.00",
                "sku": {
                    "name": "Apple iPhone 8 Plus (A1864) 64GB 金色 移动联通电信4G手机",
                    "default_image_url": "http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRZCqAUxp9AAFti6upbx41220032"
                }
            },
            ......
        ]
    }
"""

class SKUSerializer(serializers.Serializer):
    default_image_url = serializers.ImageField(source='default_image')
    name = serializers.CharField()


# class SKUSerializer(serializers.ModelSerializer):
#
#     # 新增--千万注意 ---ImageField
#     default_image_url = serializers.ImageField(source='default_image')
#
#     class Meta:
#         model = SKU
#         fields = ['name','default_image_url']

class OrderGoodsSerializer(serializers.ModelSerializer):
    sku = SKUSerializer()
    class Meta:
        model = OrderGoods
        fields = ['count','price','sku']


# 定义 详情页  序列化器
class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    # 新增 skus
    skus = OrderGoodsSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'

        # 定义 列表页  序列化器


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ['order_id', 'create_time']
