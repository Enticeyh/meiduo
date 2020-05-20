from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action

from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.order import OrderListSerializer, OrderDetailSerializer
from apps.orders.models import OrderInfo


class OrderView(ReadOnlyModelViewSet):
    # queryset = OrderInfo.objects.all()
    # serializer_class = OrderListSerializer
    pagination_class = MeiduoPagination

    # 自定义 返回 查询集
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return OrderInfo.objects.filter(order_id__contains=keyword).order_by('-create_time')
        else:
            return OrderInfo.objects.order_by('-create_time')

    # 自定义 序列器的类
    def get_serializer_class(self):

        # 判断 列表页 还是 详情页 判断条件 pk
        if 'pk' in self.kwargs:

            return OrderDetailSerializer
        else:
            return OrderListSerializer

    # 自定义 修改 订单 状态
    @action(methods=['PUT'], detail=True)
    def status(self, request, pk):

        # 1.接收参数
        order_status = request.data.get('status')

        # 2.校验
        if not order_status:
            return Response({'message': "参数不完整"}, status=400)

        # 3.修改
        # order = OrderInfo.objects.get(pk=pk)
        order = self.get_object()
        order.status = order_status
        order.save()

        # 4.返回响应对象
        return Response({
            'order_id': order.order_id,
            'status': order.status
        }, status=201)
