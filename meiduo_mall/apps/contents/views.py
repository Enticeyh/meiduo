from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories

# 1.首页 展示
class IndexView(View):
    def get(self, request):

        # 1.获取 商品分类的数据
        categories = get_categories()

        # 2.获取 广告数据
        contents = {}

        # 2.1 获取广告分类数据 所有 all()
        content_categorys = ContentCategory.objects.all()

        # 2.2 遍历 分类 id name key
        for cat in content_categorys:
            # 2.3 根据分类 获取 对应的 广告内容
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents':contents
        }

        print(contents)

        # 前后端不分离--jinja2模板渲染---后台程序员写的
        return render(request, 'index.html', context)
