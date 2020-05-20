from datetime import date
from pprint import pprint

from django import http
from django.shortcuts import render
from django.views import View
from apps.contents.utils import get_categories
from apps.goods import models
from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb


# 统计 商品访问量
class GoodsVisitView(View):
    def post(self, request, category_id):

        # 1.校验 category
        try:
            category = GoodsCategory.objects.get(pk=category_id)
        except:
            return http.HttpResponseForbidden('商品不存在!')

        # 2.判断日期 当前日期 这个分类 有没有数据
        today_date = date.today()

        # 当天 一个分类 只有一条记录
        try:
            # 如果有  count+=1
            # 1.站在  统计表的 角度 查询
            visit = GoodsVisitCount.objects.get(category=category, date=today_date)
            # 2.站在 分类的角度 查询
            # visit = category.goodsvisitcount_set.get(date=today_date)
        except:
            # 如果没有 新建 一条数据  再进行累加 count += 1
            visit = GoodsVisitCount()

        # 统一都累加
        visit.count += 1
        visit.category = category
        visit.save()

        # 3.返回响应
        return http.JsonResponse({'code': 0, 'errormsg': '记录成功!'})


# 详情页
class DetailView(View):
    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)


# 热销商品
class HotView(View):
    def get(self, request, category_id):

        # 1.校验参数
        try:
            category = GoodsCategory.objects.get(pk=category_id)
        except:
            return http.HttpResponseForbidden('商品不存在!')

        # 2.取出 销量排行 的 前两个 SKU
        hot_skus = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[0:2]

        hot_list = []
        # 3.构建前端的 数据格式
        for sku in hot_skus:
            hot_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url if sku.default_image else "",
                'price': sku.price

            })
        pprint(hot_list)
        # 4. 返回响应
        return http.JsonResponse({'code': '0', 'errmsg': 'OK', 'hot_skus': hot_list})


class ListView(View):
    def get(self, request, category_id, page_num):
        """
        :param category_id:  三级分类ID
        :param page_num:  当前页数
        """
        try:
            cat3 = GoodsCategory.objects.get(pk=category_id)
        except:
            return http.HttpResponseForbidden('商品不存在!')
        # 1.获取 商品 分类数据
        categories = get_categories()

        # 2.面包屑组件的功能
        breadcrumbs = get_breadcrumb(cat3)

        # 3. 排序 --获取 所有 SKU的值
        # 前端传入的 sort 值  和  数据库的 字段 不对应 , 所以需要代码转换
        sort = request.GET.get('sort')

        if sort == "price":
            order_field = 'price'
        elif sort == 'hot':
            order_field = '-sales'
        else:
            order_field = 'create_time'

        # 查询出来的 所有 skus
        skus = SKU.objects.filter(category=cat3, is_launched=True).order_by(order_field)

        # 1.导包分页器
        from django.core.paginator import Paginator
        # 2.实例化
        paginator = Paginator(skus, 5)
        # 3.获取 当前页的 skus数据
        page_skus = paginator.page(page_num)

        # 4.获取总个数
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'breadcrumbs': breadcrumbs,
            'sort': sort,  # 排序字段
            'category': cat3,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码

        }

        return render(request, 'list.html', context)
