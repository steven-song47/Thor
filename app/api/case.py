from . import api
from flask import jsonify, request, make_response, Flask, redirect, url_for
from ..models.project_model import *
from .. import db
from .support.project_management import *
import json


@api.route("/case/searchCases", methods=["GET"])
def search_cases():
    if request.method == "GET":
        args = request.args
        db_operate = OperateDB()
        cases = db_operate.get_cases(**args)
        data = list()
        for case in cases:
            case_id = case["id"]
            card_list = db_operate.get_card_by_case(case_id)
            card_list = [str(db_operate.get_cardIndex_by_cardID(card_id)) for card_id in card_list]
            card_str = ",".join(card_list)
            case["card"] = card_str
            case["script"] = ""
            case["bug"] = ""
            data.append(case)
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/case/uploadExcel", methods=["POST"])
def upload_cases():
    if request.method == "POST":
        excel = json.loads(request.args["excel"])
        case_list = list()
        if "Sheet1" in excel:
            case_list = excel["Sheet1"]
        if "Case List" in excel:
            case_list = excel["Case List"]
        if case_list:
            update_cases = list()
            for case in case_list:
                # "Case Content", "Level", "Card Index", "Automation", "Test Result", "Creator"是Excel表格中必填字段
                # "ID", "Tag"是非必填字段
                if {"Name", "Module", "Given", "When", "Then", "Level"} < set(case.keys()):
                    format_case = {
                        "id": case["ID"] if "ID" in case else 99999999,
                        "name": case["Name"],
                        "module": case["Module"],
                        "given": case["Given"],
                        "when": case["When"],
                        "then": case["Then"],
                        "level": case["Level"],
                        "tag": case["Tag"] if "Tag" in case else "",
                        "auto": case["Auto"] if "Auto" in case else "N",
                    }
                    update_cases.append(format_case)
                else:
                    return jsonify({"code": 200, "success": True, "error": u"存在必填字段为空"})
            db_operate = OperateDB()
            db_operate.update_cases(update_cases)
        return jsonify({"code": 200, "success": True, "error": ""})


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
            "id": case_id,
            "effect": "inactive"
        }
        db_operate = OperateDB()
        db_operate.update_cases([case])
        return jsonify({"code": 200, "success": True})


@api.route("/case/exportFiledCases", methods=["GET"])
def export_filed_cases():
    if request.method == "GET":
        db_operate = OperateDB()
        cases = db_operate.get_cases(effect="inactive")
        data = list()
        for case in cases:
            case_id = case["id"]
            card_list = db_operate.get_card_by_case(case_id)
            card_list = [str(db_operate.get_cardIndex_by_cardID(card_id)) for card_id in card_list]
            card_str = ",".join(card_list)
            case["card"] = card_str
            case["script"] = ""
            case["bug"] = ""
            data.append(case)
        return jsonify({"code": 200, "success": True, "data": data})


