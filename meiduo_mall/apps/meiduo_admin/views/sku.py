import os

from django.db.models import Q
from django.conf import settings
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKU
from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.sku import SKUSerializer


class SKUView(ModelViewSet):
    # queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = MeiduoPagination

    # 自定义 返回 结果 --搜索一个 ---没有keyword all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return SKU.objects.filter(Q(name__contains=keyword) | Q(caption__contains=keyword))
        else:
            return SKU.objects.all()

    # 自定义 删除功能--- 删除本地文件
    def destroy(self, request, *args, **kwargs):

        # 2.删除 静态文件
        # 1. 静态文件的路径
        filepath = os.path.join(settings.BASE_DIR, 'static/detail/{}.html'.format(kwargs['pk']))

        # 2.删除
        if os.path.exists(filepath):
            os.remove(filepath)

        # 3.返回
        # 1.保留 删除sku数据的功能
        return super().destroy(request, *args, **kwargs)
