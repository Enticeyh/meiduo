import json
import pickle
import base64


class CookieSecret(object):
    # 1.加密 混淆
    @classmethod
    def dumps(cls, data):

        # 1. 将 data ==> bytes
        pickle_bytes = pickle.dumps(data)

        # 2. 将 bytes == > base64
        base64_encode = base64.b64encode(pickle_bytes)

        # 3. decode()
        return base64_encode.decode()

    # 2.解密 解码
    @classmethod
    def loads(cls, data):

        # 1. 将 data ==> base64 解码
        base64_decode = base64.b64decode(data)

        # 2. 将 base64 解码的结果===> pickle ==>原始数据类型
        result = pickle.loads(base64_decode)

        return result



# data_dict = {
#     1: {
#         2: {
#             'count': 2,
#             'selected': True
#         }
#     }
# }
# #  json 作用  将 json_str 和 python dict/list 进行互转
# # json ---dict==>json_str
# json_str = json.dumps(data_dict)
#
# # json_str ===> dict
# json_dict = json.loads(json_str)
#
#
# # pickle 作用 将 对象数据 和 bytes 进行互转 --转换完毕 原始数据类型不会发生改变
# # pickle ---dict对象---bytes
# pickele_bytes = pickle.dumps(data_dict)
#
# # pickle --- bytes====dict 对象
# pickle_obj = pickle.loads(pickele_bytes)



# base64 作用 将 bytes 进行编解码 混淆
# base64_encode = base64.b64encode(pickele_bytes)

# base64 解码
# base64_decode = base64.b64decode(base64_encode)
#
# print(type(base64_encode))
# print(pickle.loads(base64_encode))
