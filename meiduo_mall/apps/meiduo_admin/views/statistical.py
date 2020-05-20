from datetime import datetime, date, timedelta

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.goods.models import GoodsVisitCount
from apps.meiduo_admin.serializers.statistical import GoodsVisitSerializer


# 6.统计 日 商品分类访问量

class UserGoodsCountView(APIView):
    def get(self, request):
        # 1.当天日期
        now_date = date.today()

        # 2.查表 GoodsVisitCount
        visits = GoodsVisitCount.objects.filter(date=now_date)

        # 3.序列化
        ser = GoodsVisitSerializer(visits, many=True)

        # 4.返回
        return Response(ser.data)


# 5.统计 用户个数 月增每天的
class UserMonthCountView(APIView):
    def get(self, request):
        # 1.当天日期
        now_date = date.today()

        # 2.取 29天前的 日期
        front_date = now_date - timedelta(days=29)

        data_list = []
        # 3.遍历 统计 每一天
        for i in range(30):
            # 3.1 当天
            current_date = front_date + timedelta(days=i)

            # 3.2 下一天
            end_date = current_date + timedelta(days=1)

            # 2.今天 增加的 用户
            count = User.objects.filter(date_joined__gte=current_date, date_joined__lt=end_date).count()

            data_list.append({
                'count': count,
                'date': current_date,
            })

        return Response(data_list)


# 4.统计 用户个数( 日下单)  day_orders
class UserOrderCountView(APIView):
    def get(self, request):
        # 1.当天日期
        now_date = date.today()

        # 2.今天 增加的 用户
        count = User.objects.filter(orderinfo__create_time__gte=now_date).distinct().count()

        return Response({
            'count': count,
            'date': now_date,
        })


# 3.统计 用户 日活数 day_active
class UserActiveCountView(APIView):
    def get(self, request):
        # 1.当天日期
        now_date = date.today()

        # 2.今天 增加的 用户
        count = User.objects.filter(last_login__gte=now_date).count()

        return Response({
            'count': count,
            'date': now_date,
        })


# 2.用户 日增个数 day_increment
class UserCreateCountView(APIView):
    def get(self, request):
        # 1.当天日期
        now_date = date.today()

        # 2.今天 增加的 用户
        count = User.objects.filter(date_joined__gte=now_date).count()

        return Response({
            'count': count,
            'date': now_date,
        })


# 1.统计 -- 用户总数
class UserTotalCountView(APIView):
    def get(self, request):
        # 1.获取当前日期
        now_date = date.today()

        # 2.统计个数
        count = User.objects.count()
        # count = User.objects.all().count()
        # 3.返回结果
        return Response({
            'count': count,
            'date': now_date
        })
