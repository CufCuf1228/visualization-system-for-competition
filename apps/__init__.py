from flask import Flask
from apps.apis import init_apis
from settings import Config

def create_app():
    # 创建app对象
    app = Flask(__name__)
    # 导入配置文件
    app.config.from_object(Config)
    # 注册api、viwes蓝图
    init_apis(app)
    # 返回app对象
    return app