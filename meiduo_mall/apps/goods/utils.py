# 封装 面包屑组件的 数据

def get_breadcrumb(cat3):
    # 1. 三级分类 cat3

    # 2.三级分类 --> 找二级
    cat2 = cat3.parent
    # 3.二级分类--->一级
    cat1 = cat2.parent
    # 商品分类 --找频道表 的 url属性
    cat1.url = cat1.goodschannel_set.all()[0].url
    #  cat1.goodschannel_set.all()= queryset [0].url

    # 返回
    return {
        'cat1':cat1,
        'cat2': cat2,
        'cat3': cat3,
    }
