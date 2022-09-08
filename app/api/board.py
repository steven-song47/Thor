from . import api
from flask import jsonify, request, make_response, Flask, redirect, url_for
from ..models.project_model import *
from .. import db
from .support.project_management import *


@api.route("/board/board", methods=["GET"])
def search_board():
    if request.method == "GET":
        data = {
            "New": [],
            "Ready for Dev": [],
            "In Dev": [],
            "Dev Done": [],
            "Testing": [],
            "Closed": [],
        }
        if "sprint" in request.args:
            sprint = request.args["sprint"]
            db_operate = OperateDB()
            if sprint == "latest":
                sprint = db_operate.get_sprints()[0]
            cases = db_operate.get_cards(sprint=sprint)
            for case in cases:
                if case["state"] == "grooming":
                    data["New"].append(case)
                elif case["state"] == "kick off":
                    data["Ready for Dev"].append(case)
                elif case["state"] in ["in dev"]:
                    data["In Dev"].append(case)
                elif case["state"] == "desk check":
                    data["Dev Done"].append(case)
                elif case["state"] == "in qa":
                    data["Testing"].append(case)
                elif case["state"] == "test done":
                    data["Closed"].append(case)
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/board/judgeSprintName", methods=["GET"])
def judge_sprint_name_unique():
    if request.method == "GET":
        result = True
        if "sprint" in request.args:
            sprint_name = request.args["sprint"]
            if sprint_name:
                db_operate = OperateDB()
                result = db_operate.judge_fields(sprint_name=sprint_name)
        return jsonify({"code": 200, "success": True, "data": result})


@api.route("/board/judgeCardIndex", methods=["GET"])
def judge_card_index_unique():
    if request.method == "GET":
        result = True
        if "index" in request.args:
            card_index = request.args["index"]
            if card_index:
                db_operate = OperateDB()
                result = db_operate.judge_fields(card_index=card_index)
        return jsonify({"code": 200, "success": True, "data": result})


@api.route("/board/getSprints", methods=["GET"])
def get_sprints():
    if request.method == "GET":
        db_operate = OperateDB()
        sprints = db_operate.get_sprints()
        return jsonify({"code": 200, "success": True, "data": sprints})


@api.route("/board/openCard", methods=["GET"])
def open_card():
    if request.method == "GET":
        card_data = dict()
        card_index = request.args["index"]
        db_operate = OperateDB()
        card_data = db_operate.get_cards(index=card_index)[0]
        card_id = card_data["id"]
        risks = db_operate.get_actions("risk", card_id)
        tasks = db_operate.get_actions("task", card_id)
        case_list = db_operate.get_case_by_card(card_id)
        cases = [db_operate.get_cases(id=case_id)[0] for case_id in case_list]
        related_cards_id = db_operate.get_card_associated_cards(card_id)
        related_cards = [db_operate.get_cards(id=card_id)[0] for card_id in related_cards_id]
        card_data["risk"] = risks
        card_data["case"] = cases
        card_data["task"] = tasks
        card_data["card"] = related_cards
        return jsonify({"code": 200, "success": True, "data": card_data})


@api.route("/board/selectMembers", methods=["GET"])
def select_members():
    if request.method == "GET":
        role = request.args["role"]
        db_operate = OperateDB()
        members = db_operate.get_members(role)
        data = [{"value": member} for member in members]
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/board/sendNotificationByWechat", methods=["POST"])
def send_by_wechat():
    if request.method == "POST":
        members = request.json["members"]
        current_state = request.json["state"]
        db_operate = OperateDB()
        phone_list = [db_operate.get_phone_by_member(member) for member in members]
        if current_state == "kick off":
            msg = "Let's have a Kick Off meeting."
        elif current_state == "desk check":
            msg = "Let's have a Desk Check meeting."
        else:
            return jsonify({"code": 200, "success": True, "err": "wrong state"})
        wechat = WechatMsg()
        err = wechat.send_msg_txt(phone_list, msg)
        if err:
            return jsonify({"code": 200, "success": True, "err": "something wrong with wechat"})
        else:
            return jsonify({"code": 200, "success": True})


@api.route("/board/switchStep", methods=["POST"])
def switch_step():
    if request.method == "POST":
        index = request.json["index"]
        step = request.json["current_state"]
        operate = request.json["operate"]
        step_list = ["grooming", "kick off", "in dev", "desk check", "in qa", "test done"]
        db_operate = OperateDB()
        card_id = db_operate.get_cardID_by_cardIndex(index)
        if operate == "next" and step != step_list[-1]:
            new_step = step_list[step_list.index(step) + 1]
        elif operate == "back" and step != step_list[0]:
            new_step = step_list[step_list.index(step) - 1]
        else:
            return jsonify({"code": 200, "success": True, "msg": "error"})
        db_operate.update_card(index, state=new_step)
        db_operate.add_changeLog(card_id, step, new_step)
        return jsonify({"code": 200, "success": True})


@api.route("/board/showOperateLog", methods=["GET"])
def show_step_log():
    if request.method == "GET":
        index = request.args["index"]
        db_operate = OperateDB()
        card_id = db_operate.get_cardID_by_cardIndex(index)
        logs = db_operate.get_changeLog(card_id)
        format_log = list()
        for log in logs:
            operate_time = log["update_time"].strftime("%Y-%m-%d %H:%M:%S")
            info_text = log["prev"] + " => " + log["current"]
            format_log.append({
                "info": info_text,
                "time": operate_time,
            })
        return jsonify({"code": 200, "success": True, "data": format_log})


@api.route("/board/updateCard", methods=["POST"])
def update_card():
    if request.method == "POST":
        index = request.json["index"]
        ac_comment = request.json["ac"]
        cases = request.json["case"]
        risks = request.json["risk"]
        tasks = request.json["task"]
        cards = request.json["card"]
        dev = None
        qa = None

        db_operate = OperateDB()
        card_id = db_operate.get_cardID_by_cardIndex(index)

        db_operate.update_card(index, ac=ac_comment)
        if "dev" in request.json:
            dev = request.json["dev"]
            db_operate.update_member_of_card(card_id, dev, "dev")
        if "qa" in request.json:
            qa = request.json["qa"]
            db_operate.update_member_of_card(card_id, qa, "qa")
        actions = list()
        updated_cases = db_operate.update_cases(cases)
        for case in updated_cases:
            db_operate.update_relationship_card_and_case(card_id, case["id"], result=case["result"])
        for risk in risks:
            # 传入参数：id, risk, state, level, type
            action = {
                "id": risk["id"],
                "risk": risk["risk"],
                "state": risk["state"],
                "level": risk["level"],
                "type": "risk",
            }
            actions.append(action)
        for task in tasks:
            # 传入参数：id, task, state, type, owner
            action = {
                "id": task["id"],
                "task": task["task"],
                "state": task["state"],
                "type": "task",
                "owner": dev,
            }
            actions.append(action)
        db_operate.update_actions(card_id, actions)
        for related_card in cards:
            related_card_id = related_card["id"]
            if related_card_id != card_id:
                db_operate.update_card_associated_cards(card1=card_id, card2=related_card_id)
        return jsonify({"code": 200, "success": True})


@api.route("/board/createCard", methods=["POST"])
def add_card():
    if request.method == "POST":
        card_data = {
            "sprint": request.json["sprint"],
            "index": request.json["index"],
            "title": request.json["title"],
            "type": request.json["type"],
            "point": request.json["point"],
            "original_link": request.json["original_link"],
        }
        if "ac" in request.json:
            card_data["ac"] = request.json["ac"]
        else:
            card_data["ac"] = None
        db_operate = OperateDB()
        db_operate.add_card(**card_data)
        return jsonify({"code": 200, "success": True})


@api.route("/board/createSprint", methods=["POST"])
def add_sprint():
    if request.method == "POST":
        name = request.json["name"]
        start_time = request.json["dateTime"][0]
        end_time = request.json["dateTime"][1]
        story_cards = request.json["storyCards"]
        task_cards = request.json["taskCards"]
        spike_cards = request.json["spikeCards"]
        bug_cards = request.json["bugCards"]
        points = request.json["points"]
        remark = ""
        if "remark" in request.json:
            remark = request.json["remark"]
        db_operate = OperateDB()
        sprint_data = {
            "name": name,
            "start_time": start_time,
            "end_time": end_time,
            "story_cards": story_cards,
            "task_cards": task_cards,
            "spike_cards": spike_cards,
            "bug_cards": bug_cards,
            "point": points,
            "remark": remark,
        }
        sprint_id = db_operate.add_sprint(**sprint_data)
        return jsonify({"code": 200, "success": True, "sprintID": sprint_id})


@api.route("/board/getAllCards", methods=["GET"])
def import_cards():
    if request.method == "GET":
        db_operate = OperateDB()
        cards = db_operate.get_cards()
        return jsonify({"code": 200, "success": True, "data": cards})