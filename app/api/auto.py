from . import api
from flask import jsonify, request, make_response, Flask, redirect, url_for
from ..models.project_model import *
from .. import db
from .support.project_management import *
import json


@api.route("/auto/listTags", methods=["GET"])
def list_tags():
    if request.method == "GET":
        db_operate = OperateDB()
        tags = db_operate.get_tags()
        tags_list = [tag[1] for tag in tags if tag[1] != []]
        tag_select = list()
        for tags in tags_list:
            tag_select += tags
        tag_select = list(set(tag_select))
        tag_data = [{"label": tag, "value": tag} for tag in tag_select]
        return jsonify({"code": 200, "success": True, "data": tag_data})


@api.route("/auto/showCases", methods=["POST"])
def show_cases():
    if request.method == "POST":
        tags = json.loads(request.args["tag"])["tag"]
        filter_case = {
            "Tag": tags,
            "Automation": "Y",
        }
        db_operate = OperateDB()
        cases = db_operate.get_cases(filter_case)
        show_cases = [{"title": "_".join([str(case["id"]), str(case["card"])]),
                       "key": "_".join([str(case["id"]), str(case["card"])])} for case in cases]
        return jsonify({"code": 200, "success": True, "data": show_cases, "filter": request.args["tag"]})
