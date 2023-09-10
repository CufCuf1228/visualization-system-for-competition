# Cuf

简单做了个可视化系统

index 页面：钢铁生产流程

数据仪表盘页面：展示各个流程用到的技术

流程分析：主要有三个图表。条形图  热力图  玫瑰图。

由于直接把技术名称放在表上会造成严重的数据重叠，因此在旁边写了个编号——名称的table

可能需要做修改的地方：

1. 图表的颜色
2. 图表上数字的大小
3. 图表布局


使用说明：

1. 电脑需要安装python
2. 下载源码后，切换到与manage.py同级的目录
3. 创建虚拟环境（命令是 python -m venv myenv）
4. 安装需求的包（命令是 pip install -r requirements.txt）
5. 配置数据文件
   1. 在与manage.py同级的目录下创建文件夹paper
   2. 在文件夹paper下放入数据 data.xlsx
   3. 或者选择进入settings文件夹下的__init__.py 修改 DATA_FILE_NAME 和 DATA_FILE_PATH 两个参数
