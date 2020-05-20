# 1.导包
from celery import Celery

# 3.加载 djadngo的配置文件
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 2.实例化
app = Celery('celery_tasks')

# 4.加载 消息队列
app.config_from_object('celery_tasks.config')

# 5. 自动查找 任务
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.detail'])
