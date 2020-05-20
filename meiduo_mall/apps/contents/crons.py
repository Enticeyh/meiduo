import os

import time
from django.conf import settings
from django.template import loader

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


# 封装  首页 页面静态化
def generate_static_index_html():

    print('%s: generate_static_index_html' % time.ctime())


    # 1.获取 首页 数据 交互数据库
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
        'contents': contents
    }

    # 2.获取 首页 的 模板文件
    template = loader.get_template('index.html')

    # 3.将数据和 模板文件 --渲染
    html_text = template.render(context)

    # 4.写入本地---本地路径
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')

    with open(file_path, 'w') as f:
        f.write(html_text)
