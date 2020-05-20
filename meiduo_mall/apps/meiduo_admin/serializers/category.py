from rest_framework import serializers

from apps.goods.models import GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        # fields = '__all__'

        fields = ['id', 'name']
