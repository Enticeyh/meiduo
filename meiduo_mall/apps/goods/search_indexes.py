# 告诉 搜索 引擎  将来 生成索引目录 的  索引是什么
from haystack import indexes
from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # 获取 模型类
    def get_model(self):
        return SKU

    # 获取 查询的  查询集
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)
