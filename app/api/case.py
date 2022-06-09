from . import api
from flask import jsonify, request, make_response, Flask, redirect, url_for
from ..models.project_model import *
from .. import db
from .support.project_management import *
import json


@api.route("/case/searchCases", methods=["GET"])
def search_cases():
    if request.method == "GET":
        table_data = list()
        args = request.args
        maps = list()
        if "level" in args:
            maps.append(Case.level == args["level"])
        elif "tag" in args:
            maps.append(Case.tag.like("%({tag})%".format(tag=args["tag"])))
        elif "card" in args:
            card_number = args["card"]
            card_id = db.session.query(Card.id).filter(Card.number == card_number).first()[0]
            maps.append(Case.card == card_id)
        elif "auto" in args:
            if args["auto"] == "Y":
                maps.append(Case.auto == True)
            elif args["auto"] == "N":
                maps.append(Case.auto == False)
        maps.append(Case.effect == "active")
        result = db.session.query(Case.id, Case.case, Case.card, Case.state, Case.level, Case.tag, Case.create_time,
                                  Case.update_time, Case.auto, Case.creator).filter(*maps).all()
        table_data = [{"id": case[0], "case": case[1],
                       "card": db.session.query(Card.number).filter(Card.id == case[2]).first()[0], "state": case[3],
                       "level": case[4], "tag": [item[1:-1] for item in case[5].split(",") if item != ''],
                       "auto": "Y" if case[8] else "N", "create_time": case[6], "update_time": case[7],
                       "creator": case[9]} for case in result]
        return jsonify({"code": 200, "success": True, "data": table_data})


@api.route("/case/uploadExcel", methods=["POST"])
def upload_cases():
    if request.method == "POST":
        excel = json.loads(request.args["excel"])
        case_list = list()
        if "Sheet1" in excel:
            case_list = excel["Sheet1"]
        elif "Case List" in excel:
            case_list = excel["Case List"]
        if case_list:
            update_cases = list()
            for case in case_list:
                # "Case Content", "Level", "Card Index", "Automation", "Test Result", "Creator"是Excel表格中必填字段
                # "ID", "Tag"是非必填字段
                if {"Case Content", "Level", "Card Index", "Automation", "Test Result", "Creator"} < set(case.keys()):
                    if "ID" not in case:
                        case["ID"] = ""
                    if "Tag" not in case:
                        case["Tag"] = ""
                    case["Automation"] = True if case["Automation"] == "Y" else False
                    update_cases.append(case)
                else:
                    return jsonify({"code": 200, "success": True, "error": u"存在必填字段为空"})
            db_operate = OperateDB()
            db_operate.update_case(update_cases)
            return jsonify({"code": 200, "success": True, "error": ""})
        else:
            return jsonify({"code": 200, "success": True, "error": u"文件有问题"})


@api.route("/case/updateCase", methods=["POST"])
def update_case():
    if request.method == "POST":
        case_id = request.args["id"]
        case = request.args["case"]
        level = request.args["level"]
        tag = request.args["tag"]
        state = request.args["result"]
        card_number = request.args["card"]
        auto = request.args["auto"]
        creator = request.args["creator"]
        case_dict = {
            "Case Content": case,
            "ID": case_id,
            "Card Index": card_number,
            "Test Result": state,
            "Level": level,
            "Tag": tag,
            "Automation": True if auto == "Y" else False,
            "Creator": creator,
        }
        db_operate = OperateDB()
        db_operate.update_case([case_dict])
        return jsonify({"code": 200, "success": True})


@api.route("/case/fileCase", methods=["POST"])
def file_case():
    if request.method == "POST":
        case_id = request.args["id"]
        case = {
            "ID": case_id,
            "Effect": "inactive"
        }
        db_operate = OperateDB()
        db_operate.update_case([case])
        return jsonify({"code": 200, "success": True})


@api.route("/case/exportFiledCases", methods=["GET"])
def export_filed_cases():
    if request.method == "GET":
        table_data = list()
        maps = list()
        maps.append(Case.effect == "inactive")
        result = db.session.query(Case.id, Case.case, Case.card, Case.state, Case.level, Case.tag, Case.create_time,
                                  Case.update_time, Case.auto, Case.creator).filter(*maps).all()
        table_data = [{"id": case[0], "case": case[1],
                       "card": db.session.query(Card.number).filter(Card.id == case[2]).first()[0], "state": case[3],
                       "level": case[4], "tag": [item[1:-1] for item in case[5].split(",") if item != ''],
                       "auto": "Y" if case[8] else "N", "create_time": case[6], "update_time": case[7],
                       "creator": case[9]} for case in result]
        return jsonify({"code": 200, "success": True, "data": table_data})


