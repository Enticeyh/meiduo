
# 自定义 jwt 响应体内容
def jwt_response_payload_handler(token, user=None, request=None):

    return {
        'token': token,
        'id':user.id,
        'username':user.username
    }
