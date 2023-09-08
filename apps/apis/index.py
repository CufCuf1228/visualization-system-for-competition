from flask import Blueprint, render_template, request
from flask_restful import Api, Resource, reqparse
import os

index_bp = Blueprint('index', __name__, url_prefix='/')

# view 前后端耦合较高
@index_bp.route('/')
def index():
    return render_template('index.html')





# apis 前后端分离用到
# class IndexApi(Resource):
#     def get(self):
#         return render_template('index.html')
    
# api = Api(index_bp)
# api.add_resource(IndexApi, '/index')