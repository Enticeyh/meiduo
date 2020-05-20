# 1.使用 itsdangerous 生成 token 和 解密
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from datetime import datetime,timedelta
import datetime

def itsdangerous_generic_token():
    #                秘钥                             token过期时间   加密方式
    ser = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600, algorithm_name="HS256")

    # 载荷
    payload = {
        'id': 10,
        'username': "laowang"
    }

    # 生成token
    token = ser.dumps(payload)

    print(token)

    # 解密
    try:
        result = ser.loads(token)
        print('解密的结果:{}'.format(result))
    except Exception as e:
        print(e)


def pyjwt_generic_token():
    # 1.载荷
    payload = {
        'id': 6,
        'username': 'admin',
        # 设置过期时间
        # 'exp': datetime.utcnow() + timedelta(hours=1)
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    import jwt
    # 2. 加密
    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')
    print(token)

    # 3.解密
    try:
        result = jwt.decode(jwt=token,key=settings.SECRET_KEY,algorithms=['HS256'])
        print('解密的结果:{}'.format(result))
    except Exception as e:
        print(e)
