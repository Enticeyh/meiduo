from django.contrib.auth.models import Permission, ContentType
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.permission import PermissionSerializer, ContentTypeSerializer


class PermissionView(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = MeiduoPagination

    # 额外的功能  查询 权限类型
    def content_types(self, request):
        types = ContentType.objects.all()
        ser = ContentTypeSerializer(types, many=True)
        return Response(ser.data)
