# 1.导包
from django_redis import get_redis_connection

from meiduo_mall.settings.dev import logger


def redis_demo():

    try:
        # 2.链接
        # ''default -参数 ---dev配置文件配置的名字
        client = get_redis_connection('default')

        # 3.增删改查
        client.set('meiduo', 'shangcheng')
    except Exception as e:
        logger.error(e)
