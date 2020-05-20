from rest_framework import serializers

from apps.users.models import User


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

        # 密码 限制  不可读
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # 增加  功能
    def create(self, validated_data):

        # 1.设置 管路员 is_staff = True
        validated_data['is_staff'] = True

        # 2.使用父类的 创建 create函数
        admin = super().create(validated_data)

        # 3.设置密码加密
        password = validated_data.get('password')
        admin.set_password(password)
        admin.save()

        return admin

    # 修改 功能
    def update(self, instance, validated_data):

        # 1.获取 修改完毕的 数据对象
        admin = super().update(instance,validated_data)

        # 2.单独 加密 密码
        password = validated_data.get('password')
        admin.set_password(password)
        admin.save()
        # 3.返回对象
        return admin

