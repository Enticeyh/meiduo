from collections import OrderedDict

from apps.goods.models import GoodsChannel


# 封装  获取 首页 商品分类数据的 函数
def get_categories():
    categories = OrderedDict()

    # 1.获取 37个 频道
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')

    # 2.遍历 37个 频道
    for channel in channels:
        # 3.获取 组id 进行分组
        group_id = channel.group_id

        # 判断 将37个 分成 11组
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 4.获取一级 分类数据对象
        cat1 = channel.category
        # 动态添加属性
        cat1.url = channel.url

        categories[group_id]['channels'].append(cat1)

        # categories[group_id]['channels'].append({
        #     'id': cat1.id,
        #     'name': cat1.name,
        #     "url": channel.url
        # })

        # 5. 获取二级分类 ---三级分类: 1:n
        for cat2 in cat1.subs.all():
            # 动态添加属性
            cat2.sub_cats = []

            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)

            categories[group_id]['sub_cats'].append(cat2)

    return categories
