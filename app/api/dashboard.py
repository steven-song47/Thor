from . import api
from flask import jsonify, request
from ..models.project_model import *
from .. import db
from .support.project_management import *


@api.route("/dashboard/dashboard", methods=["GET"])
def dashboard_data():
    if request.method == "GET":
        sprint_data = {
            "points": 0,
            "points_plan": 0,
            "points_rate": 0,
            "cards": 0,
            "cards_plan": 0,
            "cards_rate": 0,
            "sprint_detail": list()
        }
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            s = Statistical(current_sprint)
            sprint_data["points"] = s.get_sprint_done_points()
            sprint_data["points_plan"] = s.get_sprint_plan_points()
            sprint_data["points_rate"] = s.get_sprint_point_done_rate()
            sprint_data["cards"] = s.get_sprint_done_cards()
            sprint_data["cards_plan"] = s.get_sprint_plan_cards()
            sprint_data["cards_rate"] = s.get_sprint_card_done_rate()
            bugs, left_bugs, good_rate = s.get_sprint_bugs()
            sprint_data["sprint_detail"].append({
                "title": "Point overflow rate(点数溢出率)",
                "tip": "Points on all cards / Points planned",
                "value": s.get_sprint_points_overflow_rate(),
                "suffix": "%",
            })
            sprint_data["sprint_detail"].append({
                "title": "Commitment fulfillment rate(承诺达成率)",
                "tip": "Number of completed cards within a specified number of points / Number of completed cards",
                "value": s.get_sprint_card_match_points_rate(),
                "suffix": "%",
            })
            sprint_data["sprint_detail"].append({
                "title": "Good card rate(首次良卡率)",
                "tip": "Number of completed cards with no bugs / Number of completed cards",
                "value": good_rate,
                "suffix": "%",
            })
            sprint_data["sprint_detail"].append({
                "title": "Tests cost points on average(平均测试花费)",
                "tip": "",
                "value": s.get_sprint_average_qa_points(),
            })
            sprint_data["sprint_detail"].append({
                "title": "Bugs(产生Bug总数)",
                "tip": "",
                "value": bugs,
            })
            sprint_data["sprint_detail"].append({
                "title": "Left bugs(遗留Bug数)",
                "tip": "",
                "value": left_bugs,
            })
            sprint_data["sprint_detail"].append({
                "title": "Test coverage(测试覆盖率)",
                "tip": "",
                "value": "N/A",
            })
            sprint_data["sprint_detail"].append({
                "title": "Regression test pass rate(回归测试通过率)",
                "tip": "",
                "value": "N/A",
            })
        return jsonify({"code": 200, "success": True, "data": sprint_data})


@api.route("/dashboard/burnDownChart", methods=["GET"])
def burn_down_data():
    if request.method == "GET":
        points_list = list()
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            s = Statistical(current_sprint)
            points_list = s.get_sprint_points_by_day()
        return jsonify({"code": 200, "success": True, "data": points_list})


@api.route("/dashboard/cumulativeFlowChart", methods=["GET"])
def cumulative_flow_data():
    if request.method == "GET":
        step_points_list = list()
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            s = Statistical(current_sprint)
            step_points_list = s.get_sprint_step_points_by_day()
        return jsonify({"code": 200, "success": True, "data": step_points_list})


@api.route("/dashboard/cardPoints", methods=["GET"])
def card_points_data():
    if request.method == "GET":
        card_points = list()
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            s = Statistical(current_sprint)
            card_points = s.get_sprint_card_dev_qa_points()
        return jsonify({"code": 200, "success": True, "data": card_points})


@api.route("/dashboard/memberPoints", methods=["GET"])
def member_points_data():
    if request.method == "GET":
        member_points = list()
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            s = Statistical(current_sprint)
            member_points = s.get_sprint_member_done_point()
        return jsonify({"code": 200, "success": True, "data": member_points})


@api.route("/dashboard/trendData", methods=["GET"])
def trend_data():
    if request.method == "GET":
        trend_data = list()
        if "sprint" in request.args:
            if not request.args["sprint"]:
                db_operate = OperateDB()
                current_sprint = db_operate.get_sprints()[0]
            else:
                current_sprint = request.args["sprint"]
            trend_card_type = list()
            trend_done_points = list()
            trend_done_cards = list()
            trend_bugs = list()
            # current_sprint = request.args["sprint"]
            chart_type = request.args["type"]
            db_operate = OperateDB()
            sprints = db_operate.get_sprints()
            current_sprint_index = sprints.index(current_sprint)
            trend_sprints = sprints[current_sprint_index:][::-1]
            for sprint in trend_sprints:
                s = Statistical(sprint)
                sprint_done_points = s.get_sprint_done_points()
                sprint_done_cards = s.get_sprint_done_cards()
                sprint_bugs, a, b = s.get_sprint_bugs()
                sprint_card_type = s.get_sprint_card_type_num()
                trend_done_points.append({
                    "sprint": sprint,
                    "value": sprint_done_points,
                })
                trend_done_cards.append({
                    "sprint": sprint,
                    "value": sprint_done_cards,
                })
                trend_bugs.append({
                    "sprint": sprint,
                    "value": sprint_bugs,
                })
                for type_card in sprint_card_type:
                    trend_card_type.append({
                        "sprint": sprint,
                        "type": type_card["type"],
                        "value": type_card["value"],
                    })
            if chart_type == "card_group":
                trend_data = trend_card_type
            elif chart_type == "done_points":
                trend_data = trend_done_points
            elif chart_type == "done_cards":
                trend_data = trend_done_cards
            elif chart_type == "done_bugs":
                trend_data = trend_bugs
        return jsonify({"code": 200, "success": True, "data": trend_data})


