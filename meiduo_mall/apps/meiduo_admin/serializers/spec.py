from rest_framework import serializers
from apps.goods.models import SPUSpecification, SpecificationOption


# 定义SPU的 简单序列化器
class SPUSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

"""
 {
            "options": [
                {
                    "id": "选项id",
                    "name": "选项名称"
                },
                ...
            ]
        },
"""

# 定义 选项的 序列化器
class SPUOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = "__all__"


# 定义 规格的 序列化器
class SPUSpecificationSerializer(serializers.ModelSerializer):
    # spu名称 StringRelate
    spu = serializers.StringRelatedField(read_only=True)

    # 隐藏属性
    spu_id = serializers.IntegerField()

    # 新增 options 字段 -- 前端需要
    options = SPUOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = "__all__"

# class SPUSpecificationSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     spu = serializers.PrimaryKeyRelatedField(read_only=True)
#     name = serializers.CharField()

