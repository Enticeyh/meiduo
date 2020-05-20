from rest_framework import serializers

from apps.goods.models import SKUImage, SKU


# sku序列化器
class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name']


# 图片的 序列化器
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'
