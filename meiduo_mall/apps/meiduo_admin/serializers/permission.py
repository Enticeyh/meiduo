from rest_framework import serializers
from django.contrib.auth.models import Permission,ContentType


# 定义 权限类型
class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['id','name']

# 定义 权限的 序列化器
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
