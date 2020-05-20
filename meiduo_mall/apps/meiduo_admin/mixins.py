import jwt
from rest_framework.pagination import PageNumberPagination

from django.conf import settings
from django.http import HttpResponse

# 定义分页器
from rest_framework.response import Response


class MeiduoPagination(PageNumberPagination):
    # 每页 个数
    page_size = 5

    # 查询参数的 名字 --页数的参数
    page_query_param = 'page'

    # 最大个数
    max_page_size = 10

    # 自定义 返回的 分页的内容
    def get_paginated_response(self, data):
        # return Response(OrderedDict([
        #     ('count', self.page.paginator.count),
        #     ('next', self.get_next_link()),
        #     ('previous', self.get_previous_link()),
        #     ('results', data)
        # ]))

        # self 分页器对象
        # self.page 每页的对象
        # self.page.paginator django的分页器

        return Response({
            "count": self.page.paginator.count,
            "lists": data,
            "page": self.page.number,
            "pages": self.page.paginator.num_pages,
            "pagesize": self.page_size

        })


class AuthTokenMixin(object):
    def dispatch(self, request, *args, **kwargs):

        # token 请求体 传入的 token 'HTTP_AUTHORIZATION' 截取字符串 4 "JWT "
        print(request.META)
        token = request.META.get('HTTP_AUTHORIZATION')[4:]

        try:
            result = jwt.decode(token, key=settings.SECRET_KEY, algorithms=['HS256'])

        except Exception as e:
            return HttpResponse('token 校验失败')

        return super().dispatch(request, *args, **kwargs)
