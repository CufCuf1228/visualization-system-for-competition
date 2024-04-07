from flask import Blueprint, render_template, request, current_app
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, HeatMap, Pie, Scatter, Grid, Tab
from pyecharts.components import Table
from apps.apis.index import read_data, read_tech_details
import numpy as np
import math

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

        sorted_selected_data = selected_data.sort_values(by='节能成本') # sorted by tech_es_cost
        sorted_tech_names = sorted_selected_data['技术名称'].tolist()
        sorted_tech_es_potential = sorted_selected_data['节能潜力'].tolist()
        sorted_tech_es_cost = sorted_selected_data['节能成本'].tolist()
        cumulative_sum_sorted_tech_es_potential = np.cumsum(sorted_tech_es_potential)
        cumulative_sum_sorted_tech_es_potential = [round(i, 2) for i in cumulative_sum_sorted_tech_es_potential]

        grid_bar = (
            Bar(init_opts=opts.InitOpts(width="100%"))
            .add_xaxis(sorted_tech_names)
            .add_yaxis("节能成本", sorted_tech_es_cost)
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name = "节能潜力",
                    type_ ="value",
                    min_ = -(round(max(cumulative_sum_sorted_tech_es_potential)/10)*10+10),
                    max_ = round(max(cumulative_sum_sorted_tech_es_potential)/10)*10+10,
                    position = "right",
                    axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#d14a61")),
                    axislabel_opts=opts.LabelOpts(formatter="{value} kg/t"),
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="CSC曲线",pos_left="center", pos_top="5%"),
                xaxis_opts=opts.AxisOpts(name='',axislabel_opts={'show':False}),
                yaxis_opts=opts.AxisOpts(name='节能成本',axislabel_opts={"font_weight": "bold", "formatter":"{value} 元/t"},
                                         min_=round(min(sorted_tech_es_cost)-0.5),
                                         max_=round(abs(min(sorted_tech_es_cost))+0.5) if min(sorted_tech_es_cost) < abs(max(sorted_tech_es_cost)) else round(2*max(sorted_tech_es_cost))),
                datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")]
            )
        )
        grid_line = (
            Line()
            .add_xaxis(sorted_tech_names)
            .add_yaxis("节能潜力", cumulative_sum_sorted_tech_es_potential, yaxis_index=1)
        )
        grid_bar.overlap(grid_line)
        grid = Grid(init_opts=opts.InitOpts(width="100%", height="700%"))
        grid.add(grid_bar, opts.GridOpts(pos_left="10%"), is_control_axis_index=True)

        bar = (
            Bar(init_opts=opts.InitOpts(width="100%", height="700%"))
            .add_xaxis(selected_tech_names)
            .add_yaxis('节能潜力', selected_tech_es_potential)
            .add_yaxis('节能成本', selected_tech_es_cost)
            .add_yaxis('减排潜力', selected_tech_er_potential)
            .add_yaxis('减排成本', selected_tech_er_cost)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="技术条形图",pos_left="center", pos_top="5%"),
                xaxis_opts=opts.AxisOpts(name='技术编号',axislabel_opts={'show':False}),
                yaxis_opts=opts.AxisOpts(name='节能减排',axislabel_opts={"font_weight": "bold"}),
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
            legend_opts=opts.LegendOpts(pos_right='10%', orient='vertical', pos_top="center", item_width=25, item_height=18))
        )

        scatter = (
            Scatter(init_opts=opts.InitOpts(width="950%", height="700%"))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(name="减排潜力", type_="value", splitline_opts=opts.SplitLineOpts(is_show=True), name_location="end",
                                         min_=0, max_=round(max(selected_tech_er_potential)+10)),
                yaxis_opts=opts.AxisOpts(name="减排成本", type_="value", splitline_opts=opts.SplitLineOpts(is_show=True), name_location="end",
                                         min_=round(min(selected_tech_er_cost)-0.1,1), max_=round(max(selected_tech_er_cost)+0.2,1)),
                tooltip_opts=opts.TooltipOpts(is_show=False),
            )
            )
        for i in range(len(selected_tech_names)):
            scatter.add_xaxis([selected_tech_er_potential[i]])
            scatter.add_yaxis(selected_tech_names[i], [selected_tech_er_cost[i]])

        table = Table()
        headers = ["", "节能潜力\n(标煤/吨钢)", "减排潜力\n(标碳/吨钢)","节能成本\n(元/吨钢)或(元/标煤)",  "减排成本\n(元/吨钢)或(元/标碳)"]
        rows = []
        sum_selected_tech_es_potential = round(sum(selected_tech_es_potential), 2)
        sum_selected_tech_es_cost = 0
        for i in range(len(selected_tech_es_cost)):
            sum_selected_tech_es_cost += selected_tech_es_potential[i] * selected_tech_es_cost[i]
        sum_selected_tech_es_cost = round(sum_selected_tech_es_cost, 2)
        sum_selected_tech_er_potential = round(sum(selected_tech_er_potential), 2)
        sum_selected_tech_er_cost = 0
        for i in range(len(selected_tech_er_cost)):
            sum_selected_tech_er_cost += selected_tech_er_potential[i] * selected_tech_er_cost[i]
        sum_selected_tech_er_cost = round(sum_selected_tech_er_cost, 2)
        total_row = ['总计', f"{sum_selected_tech_es_potential}" + "  kg/t",
                 f"{sum_selected_tech_er_potential}" + "  kg/t",
                 f"{sum_selected_tech_es_cost}" + "  元/t",
                 f"{sum_selected_tech_er_cost}" + "  元/t"]
        rows.append(total_row)

        for select_tech_name in selected_tech_names:
            selected_row = data[data['技术名称'] == select_tech_name].values[0]
            selected_row[1] = f"{selected_row[1]}" + " kg/t"
            selected_row[2] = f"{selected_row[2]}" + " kg/t"
            selected_row[3] = f"{selected_row[3]}" + " 元/kg"
            selected_row[4] = f"{selected_row[4]}" + " 元/kg"
            rows.append(selected_row)

        table.add(headers, rows, attributes={
        "class": "my-table",
		"align": "center",
		"border": False,
		"style": "width:100%;"
	    })

        tab = Tab()
        Tab.add(tab, grid, 'CSC曲线')
        Tab.add(tab, bar, '条形图')
        Tab.add(tab, pie, '潜力饼图')
        Tab.add(tab, scatter, '减排散点图')
        Tab.add(tab, table, '总计表')

        return render_template('tech_charts.html', mytab=tab.render_embed()[:-2],
                            tech_names=tech_names, tech_details=tech_details)
    
@charts_bp.route('/CO2_pre', methods=['GET','POST'])
def CO2_pre():
    data = read_data('技术普及率')
    tech_names = data['技术名称'].tolist()
    tech_details = read_tech_details()
    CO2_emmission_data = read_data('碳排放预测')

    final_production = CO2_emmission_data['最终产量'].tolist()
    blast_furnace_percent = CO2_emmission_data['高炉占比'].tolist()
    blast_furnace_energy_cost = 569
    elc_furnace_percent = CO2_emmission_data['电炉占比'].tolist()
    elc_furnace_energy_cost = 127.01
    energy_cost_to_CO2_emmission = 2.77

    BAU_avg_steel_energy_cost = 468.69
    BAU_total_CO2_emmission = [i * BAU_avg_steel_energy_cost * energy_cost_to_CO2_emmission for i in final_production]
    
    PS_total_CO2_emmission = []
    for i in range(len(final_production)):
        PS_CO2_emmission = (blast_furnace_percent[i] * blast_furnace_energy_cost  + elc_furnace_percent[i] * elc_furnace_energy_cost ) * final_production[i] * energy_cost_to_CO2_emmission
        PS_total_CO2_emmission.append(PS_CO2_emmission)

    x_axis = CO2_emmission_data['时间'].tolist()

    if request.method == 'GET':
        LT_total_CO2_emmission = PS_total_CO2_emmission
        bar = (
            Bar(init_opts=opts.InitOpts(width="100%"))
            .add_xaxis(x_axis)
            .add_yaxis('BAU', BAU_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis('PS', PS_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis('LT', LT_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"碳排放量预测图",pos_left="center"),
                yaxis_opts=opts.AxisOpts(name='碳排放量',axislabel_opts={"font_weight": "bold"}),
                xaxis_opts=opts.AxisOpts(name='年份',axislabel_opts={'interval': 0,'rotate':0}),
                datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
                legend_opts=opts.LegendOpts(pos_left='right', orient='vertical',item_width=10, item_height=15))
        )

        return render_template('CO2_pre.html', tech_names=tech_names, tech_details=tech_details, mybar=bar.render_embed()[:-2])

    if request.method == 'POST':
        if not request.form.getlist('tech_name'):
            return render_template('CO2_pre.html', tech_names=tech_names, tech_details=tech_details)

        LT_total_CO2_emmission = []
        LT_elc_furnace_energy_cost = elc_furnace_energy_cost
        LT_blast_furnace_energy_cost = blast_furnace_energy_cost
        selected_tech_names = request.form.getlist('tech_name')
        for i in range(len(final_production)):
            for j in range(len(selected_tech_names)):
                energy_saving_potential = data[data['技术名称'] == selected_tech_names[j]]['节能潜力'].values[0]
                popularity_rate_0 = data[data['技术名称'] == selected_tech_names[j]]['普及率'].values[0]
                popularity_rate_i = (popularity_rate_0 - 0.95) * math.exp(-i*i/414) + 0.95
                if data[data['技术名称'] == selected_tech_names[j]]['高炉使用'].values[0] == 0:
                    LT_elc_furnace_energy_cost -= energy_saving_potential * popularity_rate_i
                else:
                    LT_blast_furnace_energy_cost -= energy_saving_potential * popularity_rate_i
            LS_CO2_emmssion = (LT_elc_furnace_energy_cost * elc_furnace_percent[i] + LT_blast_furnace_energy_cost * blast_furnace_percent[i]) * final_production[i] * energy_cost_to_CO2_emmission
            LT_total_CO2_emmission.append(LS_CO2_emmssion)

        bar = (
            Bar(init_opts=opts.InitOpts(width="100%"))
            .add_xaxis(x_axis)
            .add_yaxis('BAU', BAU_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis('PS', PS_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis('LT', LT_total_CO2_emmission, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"碳排放量预测图",pos_left="center"),
                yaxis_opts=opts.AxisOpts(name='碳排放量',axislabel_opts={"font_weight": "bold"}),
                xaxis_opts=opts.AxisOpts(name='年份',axislabel_opts={'interval': 0,'rotate':0}),
                datazoom_opts=[opts.DataZoomOpts(type_="slider"),opts.DataZoomOpts(type_="inside")],
                legend_opts=opts.LegendOpts(pos_left='right', orient='vertical',item_width=10, item_height=15))
        )

        return render_template('CO2_pre.html', tech_names=tech_names, tech_details=tech_details, mybar=bar.render_embed()[:-2])