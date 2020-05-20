# 1.导包
from fdfs_client.client import Fdfs_client

# 2.实例化
client = Fdfs_client('client.conf')

# 3.上传
# 文件绝对路径上传
# result = client.upload_by_filename('/Users/lpf/Downloads/gouzi.png')

# 删除 fastdfs 上的图片
# client.delete_file('group1/M00/00/02/wKharF49AvqAMXZuABKGJQkRzdc666.png')

# print(result)
"""
{

'Group name': 'group1', 
'Remote file_id': 'group1/M00/00/02/wKharF49AvqAMXZuABKGJQkRzdc666.png', 
'Status': 'Upload successed.', 
'Local file name': '/Users/lpf/Downloads/gouzi.png', 
'Uploaded size': '1.00MB', 
'Storage IP': '192.168.90.172'

}

"""
# 文件的 二进制流 -- 读取 utf8 有问题
image_file = open('/Users/lpf/Downloads/meizi.png','rb')
#
result = client.upload_by_buffer(image_file.read())
print(result)
