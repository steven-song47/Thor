# coding=utf-8
from .. import db


class ServerAPI(db.Model):
    __tablename__ = "server_api"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    server = db.Column(db.String(50))
    url = db.Column(db.String(200))
    method = db.Column(db.String(50))
    monitor = db.Column(db.Boolean)
    latest_code = db.Column(db.Integer)
    aver_res_time = db.Column(db.Float)
    aver_err_rate = db.Column(db.Float)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class APIRequestLog(db.Model):
    __tablename__ = "api_request_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, db.ForeignKey("server_api.id"))
    header = db.Column(db.Text(5000))
    params = db.Column(db.String(50))
    code = db.Column(db.Integer)
    err = db.Column(db.String(50))
    res_text = db.Column(db.Text(500))
    res_time = db.Column(db.Float)
    create_time = db.Column(db.DateTime)


class StatisticalDataforAPI(db.Model):
    __tablename__ = "statistical_data_for_api"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = start_time = db.Column(db.Date)
    normal = db.Column(db.Integer)
    auth_err = db.Column(db.Integer)
    server_err = db.Column(db.Integer)
    other_err = db.Column(db.Integer)
    rate = db.Column(db.Float)
    update_time = db.Column(db.DateTime)
