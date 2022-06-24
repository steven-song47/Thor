from . import api
from flask import jsonify, request, make_response, Flask, redirect, url_for
from .support.project_management import *


@api.route("/config/getProjects", methods=["GET"])
def get_projects():
    if request.method == "GET":
        db_operate = OperateDB()
        projects = db_operate.get_project_list()
        return jsonify({"code": 200, "success": True, "data": projects})


@api.route("/config/getProjectConfig", methods=["GET"])
def get_config():
    if request.method == "GET":
        project_config = dict()
        if "project" in request.args:
            if not request.args["project"]:
                db_operate = OperateDB()
                name = db_operate.get_project_list()[0]
            else:
                name = request.args["project"]
            db_operate = OperateDB()
            project = db_operate.get_project(name)
            if project:
                project_config = {
                    "name": project["name"],
                    "robot": project["robot"],
                    # "basic_data": [project[""], project[""]],
                    # "basic_chart": [project[""], project[""]],
                    # "extra_data": [project[""], project[""], project[""], project[""], project[""], project[""]]
                }
        return jsonify({"code": 200, "success": True, "data": project_config})


@api.route("/config/createProject", methods=["POST"])
def create_project():
    if request.method == "POST":
        name = request.json["name"]
        if "robot" in request.json:
            robot = request.json["robot"]
        else:
            robot = None
        extra_data = request.json["extra_data"]
        extra_chart = request.json["extra_chart"]
        trend_chart = request.json["trend_chart"]

        project_args = {
            "name": name,
            "robot": robot,
            "point_overflow_rate_data": True if "Point overflow rate" in extra_data else False,
            "commitment_fulfillment_rate_data": True if "Commitment fulfillment rate" in extra_data else False,
            "good_card_rate_data": True if "Good card rate" in extra_data else False,
            "average_test_costs_data": True if "Tests cost points on average" in extra_data else False,
            "bug_data": True if "Bugs" in extra_data else False,
            "left_bug_data": True if "Left bugs" in extra_data else False,
            "test_coverage_data": True if "Test coverage" in extra_data else False,
            "regression_test_data": True if "Regression test pass rate" in extra_data else False,
            "points_spent_per_card_chart": True if "Points spent per card" in extra_chart else False,
            "percentage_of_points_delivered_chart": True if "Percentage of points delivered by each member" in extra_chart else False,
            "trend_different_type_cards_chart": True if "Different type cards in Sprint" in trend_chart else False,
            "trend_completion_points_chart": True if "Completion points in Sprint" in trend_chart else False,
            "trend_completion_cards_chart": True if "Completion cards in Sprint" in trend_chart else False,
            "trend_bug_created_chart": True if "Bugs created in Sprint" in trend_chart else False,
        }
        db_operate = OperateDB()
        project_id = db_operate.add_project(**project_args)
        return jsonify({"code": 200, "success": True, "project_id": project_id})


@api.route("/config/updateProject", methods=["POST"])
def update_project():
    if request.method == "POST":
        name = request.json["name"]
        if "robot" in request.json:
            robot = request.json["robot"]
        else:
            robot = None
        extra_data = request.json["extra_data"]
        extra_chart = request.json["extra_chart"]
        trend_chart = request.json["trend_chart"]

        project_args = {
            "robot": robot,
            "point_overflow_rate_data": True if "Point overflow rate" in extra_data else False,
            "commitment_fulfillment_rate_data": True if "Commitment fulfillment rate" in extra_data else False,
            "good_card_rate_data": True if "Good card rate" in extra_data else False,
            "average_test_costs_data": True if "Tests cost points on average" in extra_data else False,
            "bug_data": True if "Bugs" in extra_data else False,
            "left_bug_data": True if "Left bugs" in extra_data else False,
            "test_coverage_data": True if "Test coverage" in extra_data else False,
            "regression_test_data": True if "Regression test pass rate" in extra_data else False,
            "points_spent_per_card_chart": True if "Points spent per card" in extra_chart else False,
            "percentage_of_points_delivered_chart": True if "Percentage of points delivered by each member" in extra_chart else False,
            "trend_different_type_cards_chart": True if "Different type cards in Sprint" in trend_chart else False,
            "trend_completion_points_chart": True if "Completion points in Sprint" in trend_chart else False,
            "trend_completion_cards_chart": True if "Completion cards in Sprint" in trend_chart else False,
            "trend_bug_created_chart": True if "Bugs created in Sprint" in trend_chart else False,
        }
        db_operate = OperateDB()
        db_operate.update_project(name, **project_args)
        return jsonify({"code": 200, "success": True})
