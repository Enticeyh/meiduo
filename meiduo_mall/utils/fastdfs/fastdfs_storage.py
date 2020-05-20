# 1.导包 文件存储类
from django.conf import settings
from django.core.files.storage import Storage


# 2. 继承
class FastDFSStorage(Storage):
    def __init__(self, base_url=None):
        self.fdfs_base_url = base_url or settings.FDFS_BASE_URL

    # 3.必须实现的函数_open 和  _save
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    # 4.重写 url  返回 带 IP:8888 的全路径
    def url(self, name):
        # http://192.168.90.172:8888/ ----- 域名
        #   group1/M00/00/01/CtM3BVrLmnaADtSKAAGlxZuk7uk4998927---name
        return self.fdfs_base_url + name

# 5. dev.py 配置文件 配置 自定义的文件存储类

# 6. 前端html 将所有 image 属性 改成 image.url
