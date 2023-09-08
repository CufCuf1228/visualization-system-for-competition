from flask import Blueprint, render_template, request, current_app
from flask_restful import Api, Resource, reqparse
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, HeatMap, Page
from jinja2.utils import markupsafe


charts_bp = Blueprint('charts', __name__, url_prefix='/charts')

# views 前后端耦合较高
@charts_bp.route('/<string:progress_name>', methods=['GET', 'POST'])
def charts(progress_name):
    data = read_data(progress_name)
    tech_name = data['技术名称'].tolist()
    tech_es_potential = data['节能潜力'].tolist() # es: energy saving ; es_potential: 节能潜力
    tech_es_cost = data['节能成本'].tolist() # es: energy reduction ; er_cost: 节能成本
    tech_er_potential = data['减排潜力'].tolist() # er: emission reduction ; er_potential: 减排潜力
    tech_er_cost = data['减排成本'].tolist() # er: emission reduction ; er_cost: 减排成本
    page = Page()
    bar = (
        Bar()
        .add_xaxis(tech_name)
        .add_yaxis('节能潜力', tech_es_potential)
        .add_yaxis('节能成本', tech_es_cost)
        .add_yaxis('减排潜力', tech_er_potential)
        .add_yaxis('减排成本', tech_er_cost)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{progress_name}流程技术分析图"),
            yaxis_opts=opts.AxisOpts(name='节能潜力/节能成本/减排潜力/减排成本'),
            xaxis_opts=opts.AxisOpts(name='技术名称',axislabel_opts={'interval': 0,'rotate':0}),
            datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
            # toolbox_opts=opts.ToolboxOpts(
            #     feature={
            #         "myComponent": {
            #             "show": True,
            #             "title": "Toggle X Axis",
            #             "icon": "path/to/icon.png",
            #             "onclick": """
            #                 function(params) {
            #                     var xAxis = chart.getOption().xAxis[0];
            #                     if (xAxis.show) {
            #                         xAxis.show = false;
            #                     } else {
            #                         xAxis.show = true;
            #                     }
            #                     chart.setOption({
            #                         xAxis: xAxis
            #                     });
            #                 }
            #             """
            #         }
            #     }
            # )
            )
    )
    column = data.columns.tolist()[1:][::-1]
    transposed_data = data.transpose()
    transposed_data = transposed_data[1:]
    transposed_data = transposed_data.values.tolist()
    print(transposed_data)
    heatmap = (
        HeatMap()
        .add_xaxis(tech_name)
        .add_yaxis('', column, transposed_data)
        .set_global_opts(
        title_opts=opts.TitleOpts(title="Heatmap"),
        xaxis_opts=opts.AxisOpts(name="Tech Name"),
        yaxis_opts=opts.AxisOpts(name="Emission Reduction Cost"),
        visualmap_opts=opts.VisualMapOpts(min_=-10, max_=10)  # 设置热力图的坐标范围
    )
    )
    page.add(bar)
    page.add(heatmap)
    return page.render_embed()


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