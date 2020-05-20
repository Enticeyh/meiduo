from pprint import pprint

from django.db import transaction
from rest_framework import serializers

from apps.goods.models import SKU, SKUSpecification
from celery_tasks.detail.tasks import get_detail_html

"""
 
        "goods": "商品SPU名称",
        "goods_id": "商品SPU ID",
        
        "category_id": "三级分类id",
        "category": "三级分类名称",
      
      
        "specs": [
            {
                "spec_id": "规格id",
                "option_id": "选项id"
            },
            ...
"""


class SKUSpecificationSerializer(serializers.ModelSerializer):
    #   # sku,spec,option 前端没有传递这些参数 所以设置成 只读
    sku = serializers.StringRelatedField(read_only=True)
    spec = serializers.StringRelatedField(read_only=True)
    option = serializers.StringRelatedField(read_only=True)

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = '__all__'


# 定义SKU 序列化器
class SKUSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()

    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    # 新增 specs
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    # 自定义增加的功能---规格选项id表要增加 --页面静态化---事务
    def create(self, validated_data):
        # 1.把 specs的数据 --剔除 pop
        specs = validated_data.pop('specs')

        # 2.使用事务 操作 sku表 SKUSpecification表 增加
        with transaction.atomic():
            sid = transaction.savepoint()

            try:
                # 1.SKU
                sku = SKU.objects.create(**validated_data)

                # 2.规格选项id表
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except Exception as e:
                print(e)

                transaction.savepoint_rollback(sid)

                return serializers.ValidationError('数据保存失败!')
            else:
                transaction.savepoint_commit(sid)

                #  执行异步任务生成新的静态页面 --worker
                get_detail_html.delay(sku.id)

                return sku

    # 自定义修改的功能---规格选项id表要增加 --页面静态化---事务
    def update(self, instance, validated_data):

        # 1.剔除 specs
        specs = validated_data.pop('specs')

        # 2.事务操作
        with transaction.atomic():
            sid = transaction.savepoint()

            try:

                # 1.修改 sku信息
                SKU.objects.filter(pk=instance.id).update(**validated_data)

                # 2.删除 老的 规格选项信息
                SKUSpecification.objects.filter(sku=instance).delete()

                # 3.新增  规格信息
                for spec in specs:
                    SKUSpecification.objects.create(sku=instance, spec_id=spec['spec_id'], option_id=spec['option_id'])

            except Exception as e:
                transaction.savepoint_rollback(sid)
                return serializers.ValidationError('数据操作失败!')

            else:
                transaction.savepoint_commit(sid)

                # 页面静态化
                get_detail_html.delay(instance.id)

                return instance


