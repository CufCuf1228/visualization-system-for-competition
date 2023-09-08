import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # 获取上级目录

class Config(object):
    # 配置文件
     DEBUG = True # 开启调试模式
     DATA_FILE_NAME = 'data.xlsx' # 数据文件名
     DATA_FILE_PATH = os.path.join(parent_dir, DATA_FILE_NAME) # 数据文件路径