from rest_framework.generics import ListAPIView

from apps.meiduo_admin.serializers.category import CategorySerializer
from apps.goods.models import GoodsCategory


class CategoryView(ListAPIView):
    serializer_class = CategorySerializer

    # 1.如果 子级 是空 代表最后 一级 ==3级
    # queryset = GoodsCategory.objects.filter(subs__isnull=True)

    # 2.如果 parent_id > 37---3级
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
