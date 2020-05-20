from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, DjangoModelPermissions

from apps.goods.models import SPUSpecification, SPU
from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.spec import SPUSpecificationSerializer, SPUSerializer


# 规格表查询 规格 --选项
class SPUSpecView(ListAPIView):
    # 添加权限控制
    permission_classes = [IsAdminUser, DjangoModelPermissions]

    serializer_class = SPUSpecificationSerializer

    # 根据 spu_id 找到对应的 规格 选项信息
    def get_queryset(self):
        # 1.获取spuid值
        pk = self.kwargs['pk']
        # 2.根据spu的id值关联过滤查询出规格信息
        return SPUSpecification.objects.filter(spu_id=pk)


# 规格表的操作--增删改
class SpecsView(ModelViewSet):
    # 添加权限控制
    permission_classes = [IsAdminUser, DjangoModelPermissions]


    # 1.内容
    queryset = SPUSpecification.objects.all()
    # 2.序列化器的类
    serializer_class = SPUSpecificationSerializer
    # 3.分页器
    pagination_class = MeiduoPagination

    # 实现 额外的 查询 spu信息
    def simple(self, request):
        # - 1.获取所有spu对象
        spus = SPU.objects.all()

        # - 2.序列化
        ser = SPUSerializer(instance=spus, many=True)

        # - 3.返回响应
        return Response(ser.data)
