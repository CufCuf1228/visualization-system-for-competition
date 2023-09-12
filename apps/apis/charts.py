from flask import Blueprint, render_template, request, current_app
from pyecharts import options as opts
from pyecharts.charts import Bar, HeatMap, Pie, Scatter, Tab
from pyecharts.components import Table
import pandas as pd
from apps.apis.index import read_data, read_tech_details


charts_bp = Blueprint('charts', __name__, url_prefix='/')


# views 前后端耦合较高
@charts_bp.route('/charts', methods=['GET'])
def charts():
    progress_name = request.args.get('progress_name')
    data = read_data(progress_name)
    tech_name = data['技术名称'].tolist()
    x_axis = [i+1 for i in range(len(tech_name))]
    tech_es_potential = data['节能潜力'].tolist() # es: energy saving ; es_potential: 节能潜力
    tech_es_cost = data['节能成本'].tolist() # es: energy reduction ; er_cost: 节能成本
    tech_er_potential = data['减排潜力'].tolist() # er: emission reduction ; er_potential: 减排潜力
    tech_er_cost = data['减排成本'].tolist() # er: emission reduction ; er_cost: 减排成本


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


    pie = (
        Pie(init_opts=opts.InitOpts(width="100%"))
        .add(
            series_name="节能潜力",
            data_pair=[list(z) for z in zip(x_axis, tech_es_potential)],
            radius=["10%", "15%"],
            center=["20%", "30%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .add(
            series_name="节能成本",
            data_pair=[list(z) for z in zip(x_axis, tech_es_cost)],
            radius=["10%", "15%"],
            center=["55%", "30%"],
            rosetype="area",
        )
        .add(
            series_name="减排潜力",
            data_pair=[list(z) for z in zip(x_axis, tech_er_potential)],
            radius=["10%", "15%"],
            center=["20%", "70%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .add(
            series_name="减排成本",
            data_pair=[list(z) for z in zip(x_axis, tech_er_cost)],
            radius=["10%", "15%"],
            center=["55%", "70%"],
            rosetype="area",
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{progress_name}流程技术玫瑰图",pos_left="center"),
                            legend_opts=opts.LegendOpts(pos_left='right', orient='vertical'),
                            )


    )

    tech_dict = list(zip(x_axis, tech_name))
    tech_details = read_tech_details()
    return render_template('charts.html', mybar=bar.render_embed()[:-2],
                            myheatmap=heatmap.render_embed()[:-2],
                            mypie=pie.render_embed()[:-2],
                            tech_dict=tech_dict,
                            tech_details=tech_details
                            )

@charts_bp.route('/tech_charts', methods=['GET','POST'])
def tech_charts():

    data = read_data('总数据')
    tech_names = data['技术名称'].tolist()
    tech_details = read_tech_details()

    if request.method == 'GET':
        return render_template('tech_charts.html', tech_names=tech_names, tech_details=tech_details)

    if request.method == 'POST':
        if not request.form.getlist('tech_name'):
            return render_template('tech_charts.html', tech_names=tech_names, tech_details=tech_details)
        selected_tech_names = request.form.getlist('tech_name')
        selected_data = data[data['技术名称'].isin(selected_tech_names)]

        selected_tech_es_potential = selected_data['节能潜力'].tolist()
        selected_tech_es_cost = selected_data['节能成本'].tolist()
        selected_tech_er_potential = selected_data['减排潜力'].tolist()
        selected_tech_er_cost = selected_data['减排成本'].tolist()


        bar = (
            Bar(init_opts=opts.InitOpts(width="100%", height="700%"))
            .add_xaxis(selected_tech_names)
            .add_yaxis('节能潜力', selected_tech_es_potential)
            .add_yaxis('节能成本', selected_tech_es_cost)
            .add_yaxis('减排潜力', selected_tech_er_potential)
            .add_yaxis('减排成本', selected_tech_er_cost)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="技术条形图",pos_left="center", pos_top="5%"),
                yaxis_opts=opts.AxisOpts(name='节能减排',axislabel_opts={"font_weight": "bold"}),
                xaxis_opts=opts.AxisOpts(name='技术编号',axislabel_opts={'interval': 0,'rotate':0}),
                datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
                legend_opts=opts.LegendOpts(pos_left='right', orient='vertical',item_width=10, item_height=15))
        )

        pie = (
        Pie(init_opts=opts.InitOpts(width="100%", height="700%"))
        .add(
            series_name="节能潜力",
            data_pair=[list(z) for z in zip(selected_tech_names, selected_tech_es_potential)],
            radius=["30%"],
            center=["20%", "30%"],
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .add(
            series_name="减排潜力",
            data_pair=[list(z) for z in zip(selected_tech_names, selected_tech_er_potential)],
            radius=["30%"],
            center=["20%", "80%"],
            label_opts=opts.LabelOpts(is_show=False, position="center"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="潜力饼图", pos_left="center", pos_top="5%"),
            legend_opts=opts.LegendOpts(pos_right='20%', orient='vertical', pos_top="center", item_width=25, item_height=18))
        )

        scatter = (
            Scatter(init_opts=opts.InitOpts(width="100%", height="700%"))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)),
                yaxis_opts=opts.AxisOpts(type_="value", axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True),),
                tooltip_opts=opts.TooltipOpts(is_show=False),
            )
        )
        for i in range(len(selected_tech_names)):
            scatter.add_xaxis([selected_tech_es_cost[i]])
            scatter.add_yaxis(selected_tech_names[i], [selected_tech_er_cost[i]])

        table = Table()
        headers = ["", "节能潜力", "节能成本", "减排潜力", "减排成本"]
        rows = [['总计', round(sum(selected_tech_es_potential),2),
                round(sum(selected_tech_es_cost),2),
                round(sum(selected_tech_er_potential),2),
                round(sum(selected_tech_er_cost),2)]]
        table.add(headers, rows,attributes={
        "class": "fl-table",
		"align": "center",
		"border": True,
		"style": "width:70vh; height:20vh;"
	    })

        tab = Tab()
        Tab.add(tab, bar, '条形图')
        Tab.add(tab, pie, '潜力饼图')
        Tab.add(tab, scatter, '成本散点图')
        Tab.add(tab, table, '总计表')
        return render_template('tech_charts.html', mytab=tab.render_embed()[:-2],
                            tech_names=tech_names, tech_details=tech_details)