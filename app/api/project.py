from . import api
from flask import jsonify, request
from ..models.project_model import *
from .. import db
from .support.project_management import *
import datetime


@api.route("/project/searchCards", methods=["GET"])
def search_cards():
    if request.method == "GET":
        table_data = list()
        args = request.args
        maps = list()
        # 查询 card、sprint两张表
        if "sprint" in args:
            maps.append(Sprint.name == args["sprint"])
        elif "index" in args:
            maps.append(Card.number == args["index"])
        elif "title" in args:
            maps.append(Card.title == args["title"])
        elif "state" in args:
            maps.append(Card.state == args["state"])
        maps.append(Card.sprint == Sprint.id)
        # 查找member
        # maps.append(Card.id == CardMemberRelationship.card)
        # maps.append(CardMemberRelationship.member == Member.id)
        result = db.session.query(Card.number, Card.title, Card.point, Card.start_time, Card.state, Sprint.name, Card.id). \
            filter(*maps).order_by(Card.update_time.desc()).all()
        for card in result:
            card_data = dict()
            card_data["sprint"] = card[5]
            card_data["index"] = card[0]
            card_data["title"] = card[1]
            card_data["point"] = card[2]
            card_data["created_at"] = card[3]
            card_data["state"] = card[4]
            card_id = card[6]
            members = db.session.query(CardMemberRelationship.member, CardMemberRelationship.role).filter(CardMemberRelationship.card == card_id).all()
            for member in members:
                if member[1] == "dev":
                    card_data["dev"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
                else:
                    card_data["qa"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
            table_data.append(card_data)
        return jsonify({"code": 200, "success": True, "data": table_data})


@api.route("/project/searchCard", methods=["GET"])
def search_card():
    if request.method == "GET":
        card_data = dict()
        card_index = request.args["index"]
        # 查询 card、sprint两张表
        card = db.session.query(Card.id, Card.number, Card.title, Card.point, Card.start_time, Card.state, Sprint.name, \
                                Card.type).filter(Card.sprint == Sprint.id).filter(Card.number == card_index).first()
        card_id = card[0]
        members = db.session.query(CardMemberRelationship.member, CardMemberRelationship.role).filter(CardMemberRelationship.card == card_id).all()
        case = db.session.query(Case.id, Case.case, Case.state).filter(Case.card == card_id).all()
        task = db.session.query(Task.id, Task.action, Task.state).filter(Task.card == card_id).all()
        bug = db.session.query(Bug.id, Bug.bug, Bug.state).filter(Bug.card == card_id).all()

        card_data["sprint"] = card[6]
        card_data["index"] = card[1]
        card_data["title"] = card[2]
        card_data["point"] = card[3]
        card_data["created_at"] = card[4]
        card_data["state"] = card[5]
        card_data["type"] = card[7]
        action = list()
        for member in members:
            if member[1] == "dev":
                card_data["dev"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
            else:
                card_data["qa"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
        for index, case_line in enumerate(case):
            line_data = dict()
            line_data["id"] = int("100" + str(case_line[0]))
            line_data["index"] = index
            line_data["type"] = "case"
            line_data["content"] = case_line[1]
            line_data["confirm"] = case_line[2]
            action.append(line_data)
        for index, task_line in enumerate(task):
            line_data = dict()
            line_data["id"] = int("101" + str(task_line[0]))
            line_data["index"] = index
            line_data["type"] = "task"
            line_data["content"] = task_line[1]
            line_data["confirm"] = task_line[2]
            action.append(line_data)
        for index, bug_line in enumerate(bug):
            line_data = dict()
            line_data["id"] = int("102" + str(bug_line[0]))
            line_data["index"] = index
            line_data["type"] = "task"
            line_data["content"] = bug_line[1]
            line_data["confirm"] = bug_line[2]
            action.append(line_data)
        card_data["action"] = action
        return jsonify({"code": 200, "success": True, "data": card_data})


@api.route("/project/createCard", methods=["POST"])
def create_card():
    data = dict()
    if request.method == "POST":
        card = Card()
        # 查询card的index是否存在
        number = Card.query.filter_by(number=request.json["card_index"]).count()
        if not Card.query.filter_by(number=request.json["card_index"]).count():
            card.number = request.json["card_index"]
            card.point = request.json["card_point"]
            card.title = request.json["card_title"]
            card.type = request.json["card_type"]
            card.start_time = get_date_format(request.json["start_time"])
            card.state = "create"
            card.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 处理dev qa
            dev_member = request.json["dev"]
            qa_member = request.json["qa"]

            # operator 预留
            card.operator = ""
            # 查询sprint是否存在
            if Sprint.query.filter_by(name=request.json["sprint_id"]).count():
                sprint_id = Sprint.query.filter_by(name=request.json["sprint_id"]).first().id
                card.sprint = sprint_id
            else:
                sprint = Sprint()
                sprint.name = request.json["sprint_id"]
                sprint.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.session.add(sprint)
                db.session.flush()
                card.sprint = sprint.id
                db.session.commit()
            db.session.add(card)
            db.session.flush()
            # 获取新建卡的id
            card_id = card.id
            db.session.commit()

            db_operate = OperateDB()
            # 添加member关系
            db_operate.add_member(card_id, dev_member)
            db_operate.add_member(card_id, qa_member)

            # 在prepare, puzzle, case, auto_case几张表中添加数据
            if "dynamic_form_case" in request.json:
                case_list = request.json["dynamic_form_case"]
                case_actions = [{"type": "case", "state": "create", "action": case} for case in case_list]
                # db_operate.add_case(case_list, card_id, "create")
                db_operate.add_actions(card_id, case_actions)
            if "dynamic_form_task" in request.json:
                task_list = request.json["dynamic_form_task"]
                # db_operate.add_task(task_list, card_id, "create")
                task_actions = [{"type": "task", "state": "create", "action": task} for task in task_list]
                db_operate.add_actions(card_id, task_actions)

            return jsonify({"code": 200, "success": True, "msg": "add card success", "card_id": card_id})
        else:
            return jsonify({"code": 200, "success": True, "msg": "card exist"})


@api.route("/project/switchCardState", methods=["POST"])
def switch_card_state():
    if request.method == "POST":
        try:
            index = request.json["index"]
            state = request.json["state"]
            card_actions = request.json["actions"]
            state_list = ["create", "grooming", "kick off", "in dev", "pr review", "desk check", "in qa", "test done"]

            db_operate = OperateDB()
            if state in state_list:
                # 修改card的状态
                result = Card.query.filter(Card.number == index).first()
                result.state = state
                db.session.commit()

                card = db.session.query(Card.id, Card.number).filter(Card.number == index).first()
                card_id = card[0]

                if "dev" in request.json:
                    dev = request.json["dev"]
                    db_operate.update_member(card_id, dev, "dev")
                if "qa" in request.json:
                    qa = request.json["qa"]
                    db_operate.update_member(card_id, qa, "qa")

                if card_actions:
                    actions = [{"id": action["id"], "action": action["content"], "state": action["confirm"], "type": action["type"]} for action
                           in card_actions]
                    print("actions: ", actions)
                    db_operate.update_actions(card_id, actions)
                return jsonify({"code": 200, "success": True, "msg": "switch state success"})
            else:
                return jsonify({"code": 200, "success": True, "msg": "wrong state"})
        except Exception as e:
            print(e)
            return jsonify({"code": 200, "success": True, "msg": "error"})


@api.route("/project/showDetail", methods=["GET"])
def show_detail():
    if request.method == "GET":
        card_data = dict()
        card_index = request.args["index"]
        # 查询 card、sprint两张表
        card = db.session.query(Card.id, Card.number, Card.title, Card.point, Card.start_time, Card.state, Sprint.name, \
                                Card.type).filter(Card.sprint == Sprint.id).filter(Card.number == card_index).first()
        card_id = card[0]
        members = db.session.query(CardMemberRelationship.member, CardMemberRelationship.role).filter(CardMemberRelationship.card == card_id).all()
        case = db.session.query(Case.case, Case.state).filter(Case.card == card_id).all()
        task = db.session.query(Task.action, Task.state).filter(Task.card == card_id).all()
        bug = db.session.query(Bug.bug, Bug.state).filter(Bug.card == card_id).all()

        card_data["sprint"] = card[6]
        card_data["index"] = card[1]
        card_data["title"] = card[2]
        card_data["point"] = card[3]
        card_data["created_at"] = card[4]
        card_data["state"] = card[5]
        card_data["type"] = card[7]
        for member in members:
            if member[1] == "dev":
                card_data["dev"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
            else:
                card_data["qa"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
        card_data["bug"] = [{"content": data[0], "status": data[1]} for data in bug]
        card_data["case"] = [{"content": data[0], "status": data[1]} for data in case]
        card_data["task"] = [{"content": data[0], "status": data[1]} for data in task]

        return jsonify({"code": 200, "success": True, "data": card_data})


@api.route("/project/getMembers", methods=["GET"])
def get_members():
    if request.method == "GET":
        role = request.args["role"]
        if role == "dev":
            result = db.session.query(Member.name).filter(Member.dev == True, Member.active == True).all()
        else:
            result = db.session.query(Member.name).filter(Member.qa == True, Member.active == True).all()
        data = [{"value": member[0]} for member in result]
        return jsonify({"code": 200, "success": True, "data": data})


