from django.conf import settings
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from fdfs_client.client import Fdfs_client

from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.mixins import MeiduoPagination
from apps.meiduo_admin.serializers.image import ImageSerializer, SKUSerializer
from celery_tasks.detail.tasks import get_detail_html


class ImageView(ModelViewSet):
    # 1.图片内容
    queryset = SKUImage.objects.all()
    # 2.序列器类
    serializer_class = ImageSerializer

    # 3.分页器
    pagination_class = MeiduoPagination

    # 添加额外的功能 简单查询 sku
    def simple(self, request):
        skus = SKU.objects.all()
        ser = SKUSerializer(skus, many=True)
        return Response(ser.data)

    # 自定义 增加的功能 --1.fsdf 2.页面静态化
    def create(self, request, *args, **kwargs):

        # 1.接受参数 sku_id image
        sku_id = request.data.get('sku')
        data = request.FILES.get('image')

        # 2.校验
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return Response({'messsage': '商品不存在!'}, status=status.HTTP_404_NOT_FOUND)

        # 3.上传图片 fdfs
        # 链接 fastdfs
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 上传图片
        result = client.upload_by_buffer(data.read())
        print(result)
        """
            'Remote file_id': 'group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg',
            'Status': 'Upload successed.',
        """
        # 4.判断上传结果
        if result['Status'] != 'Upload successed.':
            return Response({'messsage': '图片上传失败!'}, status=status.HTTP_403_FORBIDDEN)

        # 5.上传成功---更新 SKUImage的数据
        try:
            img = SKUImage.objects.create(sku=sku, image=result['Remote file_id'])
        except Exception as e:
            print(e)
            return Response({'messsage': '保存失败!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 6.页面静态化
        get_detail_html.delay(sku_id)

        # 7.返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku.id,
                'image': img.image.url
            },
            status=201
        )

    # 自定义 修改功能
    def update(self, request, *args, **kwargs):

        # 1.接收参数
        """
           请求体的参数:<QueryDict: {'sku': ['2'], 'image': [<InMemoryUploadedFile: gouzi.png (image/png)>]}>
           kwargs: {'pk': '51'}
        """
        sku_id = request.data.get('sku')
        data = request.FILES.get('image')
        img_id = kwargs.get('pk')

        # 2.校验参数
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return Response({'message': 'sku is not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            pic = SKUImage.objects.get(pk=img_id)
        except SKUImage.DoesNotExist:
            return Response({'message': 'image is not found'}, status=status.HTTP_404_NOT_FOUND)

        # 3.修改图片
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 3.1 先删除 fsatdfs 老图片
        client.delete_file(pic.image.name)

        # 3.2 再上传 新图片
        result = client.upload_by_buffer(data.read())

        # 4.判断 修改完毕的状态
        if result['Status'] != 'Upload successed.':
            return Response({'messsage': '图片上传失败!'}, status=status.HTTP_403_FORBIDDEN)

        # 5.改SKUImage数据
        upload_img_url = result['Remote file_id']
        pic.image = upload_img_url
        pic.save()

        # 6.页面静态化
        get_detail_html.delay(sku_id)

        return Response(
            {
                "id": pic.id,
                "sku": sku.id,
                "image": pic.image.url
            },
            status=201
        )


    # 自定义 删除功能
    def destroy(self, request, *args, **kwargs):

        # 1.接收参数
        img_id = kwargs['pk']

        # 2.校验
        try:
            pic = SKUImage.objects.get(pk=img_id)
        except SKUImage.DoesNotExist:
            return Response({'message':'image not found'},status=404)

        # 3.fastDFS删除图片
        client = Fdfs_client(settings.FASTDFS_PATH)
        client.delete_file(pic.image.name)

        # 4.删除image数据库数据
        pic.delete()

        # 5.返回响应
        return Response(status=204)