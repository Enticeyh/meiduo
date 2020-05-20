from rest_framework import serializers

from apps.users.models import User


# 定义 用户的 序列化器 -- 展示
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email']


# 1.没有 password字段--2. 没有 校验 操作 password 用户名 长度问题 ---增加功能
class UserAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password']
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5,
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True

            }
        }

    # 重写 create函数---密码加密问题
    def create(self, validated_data):
        # 标明 职员
        validated_data['is_staff'] = True
        return User.objects.create_user(**validated_data)
