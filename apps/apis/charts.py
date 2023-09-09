from flask import Blueprint, render_template, request, current_app
from flask_restful import Api, Resource, reqparse
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, HeatMap, Page
from pyecharts.components import Table
from pyecharts.faker import Faker
from jinja2.utils import markupsafe
import numpy as np
import random

charts_bp = Blueprint('charts', __name__, url_prefix='/charts')

# views 前后端耦合较高
@charts_bp.route('/<string:progress_name>', methods=['GET', 'POST'])
def charts(progress_name):
    data = read_data(progress_name)
    tech_name = data['技术名称'].tolist()
    x_axis = [i+1 for i in range(len(tech_name))]
    tech_es_potential = data['节能潜力'].tolist() # es: energy saving ; es_potential: 节能潜力
    tech_es_cost = data['节能成本'].tolist() # es: energy reduction ; er_cost: 节能成本
    tech_er_potential = data['减排潜力'].tolist() # er: emission reduction ; er_potential: 减排潜力
    tech_er_cost = data['减排成本'].tolist() # er: emission reduction ; er_cost: 减排成本
    page = Page(layout= Page.DraggablePageLayout)

    table = (
        Table(page_title=f"{progress_name}流程技术表格")
        .add(headers=['技术编号','技术名称'], rows=[[i+1] + row.tolist() for i, row in enumerate(pd.DataFrame(data['技术名称']).values)],
             attributes={"align": "left", "broder": "0", "width": "20%"})
    )
    print(table)
    bar = (
        Bar(init_opts=opts.InitOpts(width="80%"))
        .add_xaxis(x_axis)
        .add_yaxis('节能潜力', tech_es_potential)
        .add_yaxis('节能成本', tech_es_cost)
        .add_yaxis('减排潜力', tech_er_potential)
        .add_yaxis('减排成本', tech_er_cost)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{progress_name}流程技术条形图"),
            yaxis_opts=opts.AxisOpts(name='节能潜力/节能成本/减排潜力/减排成本'),
            xaxis_opts=opts.AxisOpts(name='技术名称',axislabel_opts={'interval': 0,'rotate':0}),
            datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
            legend_opts=opts.LegendOpts(pos_left='right'))
    )

    column = data.columns.tolist()[1:][::-1]
    heatmap = data.copy()
    # heatmap.index = tech_name
    df_stacked = heatmap.stack().reset_index()
    value = df_stacked.values.tolist()

    heatmap = (
        HeatMap(init_opts=opts.InitOpts(width="80%"))
        .add_xaxis(x_axis)
        .add_yaxis('', column, value)
        .set_global_opts(
        title_opts=opts.TitleOpts(title=f"{progress_name}流程技术热力图"),
        xaxis_opts=opts.AxisOpts(name="技术编号",axislabel_opts={'interval': 0,'rotate':0}),
        yaxis_opts=opts.AxisOpts(name="节能减排"),
        visualmap_opts=opts.VisualMapOpts(min_=-5, max_=10),  # 设置热力图的坐标范围
        legend_opts=opts.LegendOpts(pos_left='right'))
    )
    page.add(table)
    page.add(bar)
    page.add(heatmap)
    return page.render_embed()

@charts_bp.route('/1', methods=['GET', 'POST'])
def charts1():
    hm = HeatMap()
    # 使用列表表达式创建7*24的二维列表
    data = [[i,j,random.randint(10,200)] for i in range(24) for j in range(7)]
    hm.add_xaxis(Faker.clock)
    hm.add_yaxis("热力图直角坐标系",Faker.week,data)
    hm.set_global_opts(
        title_opts=opts.TitleOpts(title="热力图--显示标签"),
        visualmap_opts=opts.VisualMapOpts(
            min_=10,max_=200,
            orient="horizontal",  # 视觉映射组件水平放置
            pos_left="center"))  #居中
    hm.set_series_opts(label_opts=opts.LabelOpts(is_show=True,position="inside"))
    return hm.render_embed()


def read_data(progress_name):
    file_path = current_app.config["DATA_FILE_PATH"] # 获取数据文件路径
    data = pd.read_excel(io=file_path, sheet_name=progress_name) # 读取指定流程的数据
    return data



# apis 前后端分离用到
# class chartsApi(Resource):
#     def get(self):
#         data = {'name': 'hello world'}
#         return data

# api = Api(charts_bp)
# api.add_resource(chartsApi, '/')