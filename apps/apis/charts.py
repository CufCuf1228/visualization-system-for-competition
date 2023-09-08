from flask import Blueprint, render_template, request, current_app
from flask_restful import Api, Resource, reqparse
import pandas as pd
charts_bp = Blueprint('charts', __name__, url_prefix='/charts')

# views 前后端耦合较高
@charts_bp.route('/<string:progress_name>',methods=['GET','POST'])
def charts(progress_name):
    file_path = current_app.config["DATA_FILE_PATH"] # 获取数据文件路径
    data = pd.read_excel(io=file_path, sheet_name=progress_name) # 读取指定流程的数据
    print(data.loc[0].values)
    return progress_name






# apis 前后端分离用到
# class chartsApi(Resource):
#     def get(self):
#         data = {'name': 'hello world'}
#         return data
    
# api = Api(charts_bp)
# api.add_resource(chartsApi, '/')