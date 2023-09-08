from flask import Flask
from apps.apis.index import index_bp
from apps.apis.charts import charts_bp


def init_apis(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(charts_bp)
