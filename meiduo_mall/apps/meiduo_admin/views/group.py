from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.group import GroupSerialzier
from apps.meiduo_admin.serializers.permission import PermissionSerializer
from apps.meiduo_admin.mixins import MeiduoPagination


class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerialzier
    pagination_class = MeiduoPagination

    # 额外的功能-- 查询 权限信息
    def simple(self, request):
        perms = Permission.objects.all()
        ser = PermissionSerializer(perms, many=True)
        return Response(ser.data)
