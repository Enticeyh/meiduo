from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.admin import AdminSerializer
from apps.meiduo_admin.serializers.group import GroupSerialzier
from apps.users.models import User


class AdminView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = MeiduoPagination

    # 额外功能----用户组信息 查询
    def simple(self, request):
        group = Group.objects.all()
        ser = GroupSerialzier(group,many=True)
        return Response(ser.data)
