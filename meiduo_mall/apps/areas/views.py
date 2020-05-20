from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE

"""
    SQL
    省 select * from tb_areas where parent_id is NULL;
    市 select * from tb_areas where parent_id=130000;
    区 select * from tb_areas where parent_id=130100;
    
    ORM
    省 Area.objects.filter(parent_id__isnull=True)
    市 Area.objects.filter(parent_id=130000)
    区 Area.objects.filter(parent_id=130100)
"""


class AreaView(View):
    def get(self, request):



        # 1.area_id 查询参数
        area_id = request.GET.get('area_id')

        # 2.判断  area_id  如果 没有-- 省份
        if not area_id:

            #  如果有缓存, 就使用缓存 -- 如果没有缓存 才去交互数据库
            from django.core.cache import cache
            pro_list = cache.get('provinces')

            # 如果没有缓存 才去交互数据库
            if not pro_list:
                print('交互数据库----1遍')
                provinces = Area.objects.filter(parent_id__isnull=True)
                pro_list = [{"id": pro.id, 'name': pro.name} for pro in provinces]

                # 存缓存
                cache.set('provinces', pro_list, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': pro_list})

        # 有 --市 县
        else:

            #  如果有缓存, 就使用缓存 -- 如果没有缓存 才去交互数据库
            from django.core.cache import cache
            sub_data = cache.get('sub_%s' % area_id)

            if not sub_data:

                # 省-->市-->县---1: n
                parent = Area.objects.get(id=area_id)
                cities = parent.subs.all()

                subs = []
                for city in cities:
                    subs.append({
                        'id': city.id,
                        'name': city.name
                    })

                sub_data = {
                    "id": parent.id,
                    "parent": parent.name,
                    "subs": subs
                }

                # 存缓存
                cache.set('sub_%s' % area_id, sub_data, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
