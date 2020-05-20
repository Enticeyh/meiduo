from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views import user, statistical, spec, image, sku, category, order, permission, group, admin

urlpatterns = [
    # 1.使用 drf-jwt 实现返回token的登录功能
    url(r'^authorizations/$', obtain_jwt_token),
    # 2.自己实行登录 功能
    # url(r'^authorizations/$', user.LoginView.as_view()),

    # 3.统计 用户 的总个数
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),

    # 4.统计 用户 日增个数 day_increment
    url(r'^statistical/day_increment/$', statistical.UserCreateCountView.as_view()),

    # 5.统计 用户 日活数 day_active
    url(r'^statistical/day_active/$', statistical.UserActiveCountView.as_view()),

    # 6.统计 用户个数( 日下单)  day_orders-UserOrderCountView
    url(r'^statistical/day_orders/$', statistical.UserOrderCountView.as_view()),

    # 7.统计 用户个数 月增每天的 day_orders-UserMonthCountView
    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),

    # 8.统计 日 商品分类访问量UserGoodsCountView
    url(r'^statistical/goods_day_views/$', statistical.UserGoodsCountView.as_view()),


    # 9.用户管理 users/
    url(r'^users/$', user.UsersCountView.as_view()),

    # 10.查询 简单SPU 信息
    url(r'^goods/simple/$', spec.SpecsView.as_view({'get': 'simple'})),

    # 11.查询 简单 SKU信息 skus/simple/
    # url(r'^skus/simple/$', sku.SKUView.as_view()),
    url(r'^skus/simple/$', image.ImageView.as_view({'get': 'simple'})),

    # 12 查询 第三级分类 信息 skus/categories/
    url(r'^skus/categories/$', category.CategoryView.as_view()),

    # 13. SPU 规格信息 查询 goods/(?P<pk>\d+)/specs/
    url(r'^goods/(?P<pk>\d+)/specs/$', spec.SPUSpecView.as_view()),

    # 14. 查询 权限 类型
    url(r'^permission/content_types/$', permission.PermissionView.as_view({'get': 'content_types'})),

    # 15. 查询 权限 信息数据
    url(r'^permission/simple/$', group.GroupView.as_view({'get': 'simple'})),

    # 16. 查询 用户组 信息
    url(r'^permission/groups/simple/$', admin.AdminView.as_view({'get': 'simple'})),

]

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# 注册路由
router.register(r'goods/specs', spec.SpecsView, 'specs')
# 图片路由
router.register(r'skus/images', image.ImageView, 'images')
# SKU路由
router.register(r'skus', sku.SKUView, 'sku')

# 订单路由
router.register(r'orders', order.OrderView, 'orders')

# 权限 路由 permission/perms/
router.register(r'permission/perms', permission.PermissionView, 'perms')

# 用户组 路由 permission/groups/
router.register(r'permission/groups', group.GroupView, 'group')

# 管理员 路由
router.register(r'permission/admins', admin.AdminView, 'perms_admin')

print(router.urls)
# 添加路由
urlpatterns += router.urls
