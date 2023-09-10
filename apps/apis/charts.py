from flask import Blueprint, render_template, request, current_app, url_for
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, HeatMap, Pie, Page


charts_bp = Blueprint('charts', __name__, url_prefix='/')

# views 前后端耦合较高
@charts_bp.route('/charts', methods=['GET', 'POST'])
def charts():
    if request.method == 'GET':
        progress_name = request.args.get('progress_name')
        data = read_data(progress_name)
        tech_name = data['技术名称'].tolist()
        x_axis = [i+1 for i in range(len(tech_name))]
        tech_es_potential = data['节能潜力'].tolist() # es: energy saving ; es_potential: 节能潜力
        tech_es_cost = data['节能成本'].tolist() # es: energy reduction ; er_cost: 节能成本
        tech_er_potential = data['减排潜力'].tolist() # er: emission reduction ; er_potential: 减排潜力
        tech_er_cost = data['减排成本'].tolist() # er: emission reduction ; er_cost: 减排成本
        # page = Page()

        bar = (
            Bar(init_opts=opts.InitOpts(width="100%"))
            .add_xaxis(x_axis)
            .add_yaxis('节能潜力', tech_es_potential)
            .add_yaxis('节能成本', tech_es_cost)
            .add_yaxis('减排潜力', tech_er_potential)
            .add_yaxis('减排成本', tech_er_cost)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{progress_name}流程技术条形图",pos_left="center"),
                yaxis_opts=opts.AxisOpts(name='节能减排',axislabel_opts={"font_weight": "bold"}),
                xaxis_opts=opts.AxisOpts(name='技术编号',axislabel_opts={'interval': 0,'rotate':0}),
                datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
                legend_opts=opts.LegendOpts(pos_left='right', orient='vertical',item_width=10, item_height=15))
        )

        column = data.columns.tolist()[1:][::-1]
        heatmap = data.copy()
        df_stacked = heatmap.stack().reset_index()
        value = df_stacked.values.tolist()
        heatmap = (
            HeatMap(init_opts=opts.InitOpts(width="100%"))
            .add_xaxis(x_axis)
            .add_yaxis('', column, value)
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{progress_name}流程技术热力图", pos_left="center"),
            xaxis_opts=opts.AxisOpts(name="技术编号",axislabel_opts={'interval': 0,'rotate':0}),
            yaxis_opts=opts.AxisOpts(name="节能减排"),
            visualmap_opts=opts.VisualMapOpts(min_=-2, max_=10),  # 设置热力图的坐标范围
            legend_opts=opts.LegendOpts(pos_left='left'),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")])
        )
        # page.add(table)
        # page.add(bar)
        # page.add(heatmap)
        # page.render()

        pie = (
            Pie(init_opts=opts.InitOpts(width="100%"))
            .add(
                series_name="节能潜力",
                data_pair=[list(z) for z in zip(x_axis, tech_es_potential)],
                radius=["10%", "20%"],
                center=["20%", "30%"],
                rosetype="radius",
                label_opts=opts.LabelOpts(is_show=False, position="center"),
            )
            .add(
                series_name="节能成本",
                data_pair=[list(z) for z in zip(x_axis, tech_es_cost)],
                radius=["10%", "20%"],
                center=["55%", "30%"],
                rosetype="area",
            )
            .add(
                series_name="减排潜力",
                data_pair=[list(z) for z in zip(x_axis, tech_er_potential)],
                radius=["10%", "20%"],
                center=["20%", "70%"],
                rosetype="radius",
                label_opts=opts.LabelOpts(is_show=False, position="center"),
            )
            .add(
                series_name="减排成本",
                data_pair=[list(z) for z in zip(x_axis, tech_er_cost)],
                radius=["10%", "20%"],
                center=["55%", "70%"],
                rosetype="area",
            )
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{progress_name}流程技术玫瑰图",pos_left="center"),
                             legend_opts=opts.LegendOpts(pos_left='right', orient='vertical'),
                             )
                             
            
        )

        tech_dict = list(zip(x_axis, tech_name))
        print(tech_dict)
        return render_template('charts.html', mybar=bar.render_embed()[:-2],
                               myheatmap=heatmap.render_embed()[:-2],
                               mypie=pie.render_embed()[:-2],
                               tech_dict=tech_dict
                               )


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