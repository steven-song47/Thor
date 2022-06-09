from . import api
from flask import jsonify, request
from ..models.project_model import *
from .. import db
from .support.project_management import *


@api.route("/chart/sprint", methods=["GET"])
def show_latest_sprint():
    # 获取最近5轮sprint的已完成的点数
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        latest_sprint = sprint_sort_list[0]
        sprint_id = latest_sprint[0]
        sprint_name = latest_sprint[1]
        card_list = db.session.query(Card.point, Card.state, Card.id).filter(Card.sprint == sprint_id).all()
        total_card_num = len(card_list)
        total_point = sum([card[0] for card in card_list])
        finish_card_num = sum([1 for card in card_list if card[1] == "test done"])
        finish_point = sum([card[0] for card in card_list if card[1] == "test done"])
        total_bug_num = 0
        left_bug_num = 0
        for card in card_list:
            card_id = card[2]
            bug_list = db.session.query(Bug.state).filter(Bug.card == card_id).all()
            card_bug_num = len(bug_list)
            left_num = sum([1 for bug in bug_list if bug[0] != "complete"])
            total_bug_num += card_bug_num
            left_bug_num += left_num
        data = {
            "sprint_name": sprint_name,
            "finish_card": finish_card_num,
            "finish_card_percent": "%.2f%%" % (finish_card_num/total_card_num*100),
            "finish_point": finish_point,
            "finish_point_percent": "%.2f%%" % (finish_point/total_point*100),
            "total_bug": total_bug_num,
            "left_bug": left_bug_num,
        }
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/chart/point", methods=["GET"])
def points_area():
    # 获取最近5轮sprint的已完成的点数
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        for index, sprint in enumerate(sprint_sort_list):
            if index < 5:
                sprint_id = sprint[0]
                sprint_name = sprint[1]
                card_list = db.session.query(Card.point, Card.state).filter(Card.sprint == sprint_id).all()
                sprint_point = 0
                for card in card_list:
                    if card[1] == "test done":
                        sprint_point += card[0]
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": sprint_point,
                })
            else:
                break
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/chart/card", methods=["GET"])
def cards_line():
    # 获取最近5轮sprint的已完成的card的数量
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        for index, sprint in enumerate(sprint_sort_list):
            if index < 5:
                sprint_id = sprint[0]
                sprint_name = sprint[1]
                card_list = db.session.query(Card.state).filter(Card.sprint == sprint_id).all()
                sprint_card = 0
                for card in card_list:
                    if card[0] == "test done":
                        sprint_card += 1
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": sprint_card
                })
            else:
                break
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/chart/cardGroup", methods=["GET"])
def card_group_column():
    # 获取最近5轮sprint的已完成的card的分组数量
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        for index, sprint in enumerate(sprint_sort_list):
            if index < 5:
                sprint_id = sprint[0]
                sprint_name = sprint[1]
                card_list = db.session.query(Card.state, Card.type).filter(Card.sprint == sprint_id).all()
                type_list = ["normal", "spike", "bug", "task"]
                normal_num, spike_num, bug_num, task_num = 0, 0, 0, 0
                for card in card_list:
                    if card[0] == "test done":
                        if card[1] == "normal":
                            normal_num += 1
                        elif card[1] == "spike":
                            spike_num += 1
                        elif card[1] == "bug":
                            bug_num += 1
                        elif card[1] == "task":
                            task_num += 1
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": task_num,
                    "type": "Task",
                })
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": bug_num,
                    "type": "Bug",
                })
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": spike_num,
                    "type": "Spike",
                })
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": normal_num,
                    "type": "Normal",
                })
            else:
                break
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/chart/bug", methods=["GET"])
def bugs_column():
    # 获取最近5轮sprint的bug的数量
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        for index, sprint in enumerate(sprint_sort_list):
            if index < 5:
                sprint_id = sprint[0]
                sprint_name = sprint[1]
                card_list = db.session.query(Card.id).filter(Card.sprint == sprint_id).all()
                unsolve = 0
                solve = 0
                for card in card_list:
                    card_id = card[0]
                    bug_list = db.session.query(Bug.state).filter(Bug.card == card_id).all()
                    for bug in bug_list:
                        if bug[0] == "complete":
                            solve += 1
                        else:
                            unsolve += 1
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": unsolve,
                    "type": "Unsolved"
                })
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": solve,
                    "type": "Solved"
                })
            else:
                break
        return jsonify({"code": 200, "success": True, "data": data})


@api.route("/chart/case", methods=["GET"])
def cases_column():
    # 获取最近5轮sprint的case的数量
    if request.method == "GET":
        data = list()
        sprint_list = db.session.query(Sprint.id, Sprint.name, Sprint.update_time).all()
        sprint_sort_list = sorted(sprint_list, key=lambda sprint: datetimeStr_switch_int(sprint[2]), reverse=True)
        for index, sprint in enumerate(sprint_sort_list):
            if index < 5:
                sprint_id = sprint[0]
                sprint_name = sprint[1]
                card_list = db.session.query(Card.id).filter(Card.sprint == sprint_id).all()
                case_num = 0
                for card in card_list:
                    card_id = card[0]
                    card_case_num = Case.query.filter_by(card=card_id).count()
                    case_num += card_case_num
                data.insert(0, {
                    "sprint": sprint_name,
                    "value": case_num,
                })
            else:
                break
        return jsonify({"code": 200, "success": True, "data": data})