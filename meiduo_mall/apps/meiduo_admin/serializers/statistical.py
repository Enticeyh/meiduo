from rest_framework import serializers

# 商品分类
from apps.goods.models import GoodsVisitCount


class GoodsVisitSerializer(serializers.Serializer):
    category = serializers.StringRelatedField(read_only=True)
    count = serializers.IntegerField()


# class GoodsVisitSerializer(serializers.ModelSerializer):
#     category = serializers.StringRelatedField(read_only=True)
#     class Meta:
#         model = GoodsVisitCount
#         fields = ['count', 'category']
