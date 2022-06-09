from . import api
from flask import jsonify, request
from ..models.project_model import *
from .. import db
from .support.project_management import *


@api.route("/member/addMember", methods=["POST"])
def add_member():
    if request.method == "POST":
        add_data = {
            "name": request.json["name"],
            "role": request.json["role"],
        }
        if "email" in request.json:
            add_data["email"] = request.json["email"]
        if "phone" in request.json:
            add_data["phone"] = request.json["phone"]
        db_operate = OperateDB()
        member_id = db_operate.add_project_member(**add_data)
        return jsonify({"code": 200, "success": True, "member_id": member_id})


@api.route("/member/searchMembers", methods=["GET"])
def search_members():
    if request.method == "GET":
        args = request.args
        search_filters = dict()
        if "name" in args:
            search_filters["name"] = args["name"]
        elif "active" in args:
            search_filters["active"] = args["active"]
        db_operate = OperateDB()
        members = db_operate.get_project_members(**search_filters)
        return jsonify({"code": 200, "success": True, "data": members})


@api.route("/member/getMember", methods=["GET"])
def get_member():
    if request.method == "GET":
        data = dict()
        name = request.args["name"]
        member = db.session.query(Member.id, Member.dev, Member.qa, Member.active).filter(Member.name == name).first()
        data["id"] = member[0]
        data["name"] = name
        if member[1] is True and member[2] is False:
            data["role"] = "DEV"
        elif member[1] is False and member[2] is True:
            data["role"] = "QA"
        if member[3] is True:
            data["active"] = "Active"
        else:
            data["active"] = "Inactive"
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/member/updateMember", methods=["POST"])
def update_member():
    if request.method == "POST":
        name = request.json["name"]
        update_data = dict()
        if "role" in request.json:
            update_data["role"] = request.json["role"]
        if "email" in request.json:
            update_data["email"] = request.json["email"]
        if "phone" in request.json:
            update_data["phone"] = request.json["phone"]
        db_operate = OperateDB()
        db_operate.update_project_member(name, **update_data)
        return jsonify({"code": 200, "success": True})


@api.route("/member/deleteMember", methods=["POST"])
def delete_members():
    if request.method == "POST":
        name = request.json["name"]
        update_data = {
            "active": "Inactive",
        }
        db_operate = OperateDB()
        db_operate.update_project_member(name, **update_data)
        return jsonify({"code": 200, "success": True})
