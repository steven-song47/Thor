from ... import db
from ...models.project_model import *
import re, random, datetime, time, requests, json
from operator import or_, and_
from functools import reduce
from ... import db


class OperateDB:

    def __init__(self):
        pass

    def _or_filter(self, filters):
        return reduce(lambda x, y: or_(x, y), filters)

    def _get_action_id(self, o_id):
        if type(o_id) == str:
            return "new"
        else:
            return o_id

    def _check_case_exist(self, case_id):
        result = False
        if isinstance(case_id, str):
            case_id = int(case_id)
        if isinstance(case_id, int):
            if Case.query.filter_by(id=case_id).count():
                result = True
        return result

    def _tag_str_to_db(self, tag_str):
        tag_list = tag_str.split(",")
        tag_list = ["(" + tag + ")" for tag in tag_list if tag != '']
        tag = ",".join(tag_list)
        return tag

    def _tag_db_to_str(self, tag):
        tag_str = ""
        if tag is not None:
            tag_list = tag.split(",")
            tag_list = [tag[1:-1] for tag in tag_list if tag != '']
            tag_str = ",".join(tag_list)
        return tag_str

    def get_tags(self):
        tags = db.session.query(Case.id, Case.tag, Case.auto).all()
        tag_result = list()
        for tag in tags:
            tag_list = [t[1:-1] for t in tag[1].split(",") if t != '']
            tag_result.append([tag[0], tag_list, tag[2]])
        return tag_result

    def get_sprints(self):
        sprints = db.session.query(Sprint.name).order_by(Sprint.create_time.desc()).all()
        sprints = [sprint[0] for sprint in sprints]
        return sprints

    def judge_fields(self, **args):
        result = False
        if "sprint_name" in args:
            result = False if Sprint.query.filter(Sprint.name == args["sprint_name"]).count() else True
        if "card_index" in args:
            result = False if Card.query.filter(Card.number == args["card_index"]).count() else True
        return result

    def get_sprintID_by_sprintName(self, sprint_name):
        sprint = db.session.query(Sprint.id).filter(Sprint.name == sprint_name).first()
        if sprint:
            sprint_id = sprint[0]
        else:
            sprint_id = ""
        return sprint_id

    def get_sprint_data(self, **args):
        maps = list()
        if "sprint_id" in args:
            maps.append(Sprint.id == args["sprint_id"])
        if "sprint_name" in args:
            maps.append(Sprint.name == args["sprint_name"])
        sprint_data = db.session.query(Sprint.id, Sprint.name, Sprint.create_time, Sprint.start_time, Sprint.end_time,
                                       Sprint.point, Sprint.story_cards, Sprint.spike_cards, Sprint.bug_cards,
                                       Sprint.task_cards).filter(*maps).all()
        sprint_data = [{"id": sprint[0], "name": sprint[1], "create_time": sprint[2], "start_time": sprint[3],
                        "end_time": sprint[4], "points": sprint[5], "story_cards": sprint[6], "spike_cards": sprint[7],
                        "bug_cards": sprint[8], "task_cards": sprint[9]} for sprint in sprint_data]
        return sprint_data

    def add_sprint(self, **args):
        sprint_id = ""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            sprint = Sprint()
            sprint.name = args["name"]
            sprint.create_time = now_time
            sprint.start_time = args["start_time"]
            sprint.end_time = args["end_time"]
            sprint.point = args["point"]
            sprint.story_cards = args["story_cards"]
            sprint.spike_cards = args["spike_cards"]
            sprint.task_cards = args["task_cards"]
            sprint.bug_cards = args["bug_cards"]
            sprint.remark = args["remark"]
            db.session.add(sprint)
            db.session.flush()
            sprint_id = sprint.id
            db.session.commit()
            db.session.close()
        except:
            db.session.close()
        return sprint_id

    def get_cardID_by_cardIndex(self, index):
        card = db.session.query(Card.id).filter(Card.number == index).first()
        if card:
            card_id = card[0]
        else:
            card_id = ""
        return card_id

    def get_cardIndex_by_cardID(self, card_id):
        card_index = ""
        card = db.session.query(Card.number).filter(Card.id == card_id).first()
        if card:
            card_index = card[0]
        return card_index

    def get_actions(self, action_type, card_id):
        actions = list()
        if action_type == "risk":
            risk = db.session.query(Risk.id, Risk.risk, Risk.state, Risk.level).filter(Risk.card == card_id).all()
            for index, line in enumerate(risk):
                line_data = dict()
                line_data["id"] = line[0]
                line_data["index"] = index
                line_data["risk"] = line[1]
                line_data["state"] = line[2]
                line_data["level"] = line[3]
                actions.append(line_data)
        # elif action_type == "case":
        #     case = db.session.query(Case.id, Case.case, Case.state, Case.auto, Case.level).filter(Case.card == card_id).all()
        #     for index, line in enumerate(case):
        #         line_data = dict()
        #         line_data["id"] = line[0]
        #         line_data["index"] = index
        #         line_data["case"] = line[1]
        #         line_data["state"] = line[2]
        #         line_data["auto"] = "Y" if line[3] else "N"
        #         line_data["level"] = line[4]
        #         actions.append(line_data)
        elif action_type == "bug":
            bug = db.session.query(Bug.id, Bug.bug, Bug.state, Bug.level).filter(Bug.card == card_id).all()
            for index, line in enumerate(bug):
                line_data = dict()
                line_data["id"] = line[0]
                line_data["index"] = index
                line_data["bug"] = line[1]
                line_data["state"] = line[2]
                line_data["level"] = line[3]
                actions.append(line_data)
        elif action_type == "task":
            task = db.session.query(Task.id, Task.action, Task.state).filter(Task.card == card_id).all()
            for index, line in enumerate(task):
                line_data = dict()
                line_data["id"] = line[0]
                line_data["index"] = index
                line_data["task"] = line[1]
                line_data["state"] = line[2]
                actions.append(line_data)
        else:
            pass
        return actions

    def add_actions(self, card_id, actions):
        err_msg = ""
        action_list = list()
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for action in actions:
            if "type" in action:
                if action["type"] == "task":
                    # 传入参数：task, state, type, owner
                    task = Task()
                    task.action = action["task"]
                    task.card = card_id
                    task.state = action["state"]
                    task.owner = action["owner"]
                    task.update_time = now_time
                    task.create_time = now_time
                    action_list.append(task)
                # elif action["type"] == "case":
                #     # 传入参数：case, state, level, type, auto, creator
                #     case = Case()
                #     case.case = action["case"]
                #     case.card = card_id
                #     case.state = action["state"]
                #     case.update_time = now_time
                #     case.create_time = now_time
                #     case.level = action["level"]
                #     case.effect = "active"
                #     case.tag = ""
                #     case.auto = True if action["auto"] == "Y" else False
                #     case.creator = action["creator"]
                #     action_list.append(case)
                elif action["type"] == "bug":
                    # 传入参数：bug, state, level, type, owner, tester
                    bug = Bug()
                    bug.bug = action["bug"]
                    bug.card = card_id
                    bug.state = action["state"]
                    bug.update_time = now_time
                    bug.create_time = now_time
                    bug.owner = action["owner"]
                    bug.tester = action["tester"]
                    bug.level = action["level"]
                    action_list.append(bug)
                elif action["type"] == "risk":
                    print("risk action: ", action)
                    # 传入参数：risk, state, level, type
                    risk = Risk()
                    risk.risk = action["risk"]
                    risk.card = card_id
                    risk.state = action["state"]
                    risk.level = action["level"]
                    risk.create_time = now_time
                    risk.update_time = now_time
                    action_list.append(risk)
                else:
                    err_msg = "action type is not correct!"
            else:
                err_msg = "type is not in action!"
        db.session.add_all(action_list)
        db.session.commit()
        db.session.close()
        return err_msg

    def update_actions(self, card_id, actions):
        for action in actions:
            action_id = action["id"]
            action_id = self._get_action_id(action_id)
            if action_id == "new":
                # print("new action: ", action)
                self.add_actions(card_id, [action])
            else:
                # id action state
                update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if action["type"] == "task":
                    res = db.session.query(Task).filter(Task.id == action_id).update(
                        {"action": action["task"], "state": action["state"], "update_time": update_time})
                    db.session.commit()
                # elif action["type"] == "case":
                #     res = db.session.query(Case).filter(Case.id == action_id).update(
                #         {"case": action["case"], "state": action["state"], "update_time": update_time,
                #          "level": action["level"], "auto": True if action["auto"] == "Y" else False})
                #     db.session.commit()
                elif action["type"] == "bug":
                    res = db.session.query(Bug).filter(Bug.id == action_id).update(
                        {"bug": action["bug"], "state": action["state"], "update_time": update_time,
                         "level": action["level"]})
                    db.session.commit()
                elif action["type"] == "risk":
                    res = db.session.query(Risk).filter(Risk.id == action_id).update(
                        {"risk": action["risk"], "state": action["state"], "update_time": update_time,
                         "level": action["level"]})
                    db.session.commit()
        db.session.close()

    def add_member(self, card_id, member_name):
        member = db.session.query(Member.id, Member.dev, Member.qa).filter(Member.name == member_name).first()
        member_id = member[0]
        membership = CardMemberRelationship()
        membership.card = card_id
        membership.member = member_id
        if member[1] is True and member[2] is False:
            membership.role = "dev"
        elif member[1] is False and member[2] is True:
            membership.role = "qa"
        membership.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        membership.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(membership)
        db.session.commit()
        db.session.close()

    def update_member(self, card_id, member_name, role):
        member = db.session.query(Member.id).filter(Member.name == member_name).first()
        member_id = member[0]
        if not CardMemberRelationship.query.filter_by(card=card_id, role=role).count():
            self.add_member(card_id, member_name)
        else:
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.query(CardMemberRelationship).filter(CardMemberRelationship.card == card_id,
                                                            CardMemberRelationship.role == role).update(
                {"member": member_id, "update_time": update_time})
            db.session.commit()
            db.session.close()

    def get_phone_by_member(self, name):
        member = db.session.query(Member.phone).filter(Member.name == name).firtst()
        phone = member[0]
        return phone

    def get_members(self, role):
        if role == "dev":
            members = db.session.query(Member.name).filter(Member.dev == True, Member.active == True).all()
        elif role == "qa":
            members = db.session.query(Member.name).filter(Member.qa == True, Member.active == True).all()
        elif role == "tech":
            members = db.session.query(Member.name).filter(Member.dev == True, Member.active == True).all()
        elif role == "ba":
            members = db.session.query(Member.name).filter(Member.ba == True, Member.active == True).all()
        else:
            members = db.session.query(Member.name).filter(Member.active == True).all()
        members = [member[0] for member in members]
        return members

    def add_case(self, **args):
        case_id = ""
        if set(args.keys()).issuperset({"name", "module", "given", "when", "then", "level", "tag", "auto"}):
            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                case = Case()
                case.name = args["name"]
                case.module = args["module"]
                case.given = args["given"]
                case.when = args["when"]
                case.then = args["then"]
                case.level = args["level"]
                case.tag = self._tag_str_to_db(args["tag"])
                case.auto = True if args["auto"] == "Y" else False
                case.update_time = now_time
                case.create_time = now_time
                case.review = "created"
                case.effect = "active"
                # case.result = "Created"
                case.result = args["result"]
                case.creator = None
                db.session.add(case)
                db.session.flush()
                case_id = case.id
                db.session.commit()
                db.session.close()
            except Exception as e:
                print(e)
        else:
            print("[func:add_case] 参数不匹配")
        return case_id

    def update_cases(self, cases):
        updated_cases = list()
        for case in cases:
            if "id" in case:
                if not self._check_case_exist(case["id"]):
                    case_id = self.add_case(**case)
                    case["id"] = case_id
                    updated_cases.append(case)
                else:
                    update_sql = dict()
                    # case["id"]存在传入的是个string的情况
                    case_id = int(case["id"])
                    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if "name" in case:
                        update_sql["name"] = case["name"]
                    if "module" in case:
                        update_sql["module"] = case["module"]
                    if "given" in case:
                        update_sql["given"] = case["given"]
                    if "when" in case:
                        update_sql["when"] = case["when"]
                    if "then" in case:
                        update_sql["then"] = case["then"]
                    if "level" in case:
                        update_sql["level"] = case["level"]
                    if "tag" in case:
                        update_sql["tag"] = self._tag_str_to_db(case["tag"])
                    if "auto" in case:
                        update_sql["auto"] = True if case["auto"] == "Y" else False
                    if "review" in case:
                        update_sql["review"] = case["review"]
                    if "effect" in case:
                        update_sql["effect"] = case["effect"]
                    if "result" in case:
                        update_sql["result"] = case["result"]
                    update_sql["update_time"] = now_time
                    try:
                        db.session.query(Case).filter(Case.id == case_id).update(update_sql)
                        db.session.commit()
                        updated_cases.append(case)
                    except Exception as e:
                        print("[ERROR] case_id: %s update fail (%s)" % (case_id, e))
        return updated_cases

    def get_cases(self, **filters):
        filter_maps = list()
        cases = list()
        if "id" in filters:
            filter_maps.append(Case.id == filters["id"])
        if "name" in filters:
            filter_maps.append(Case.name == filters["name"])
        if "module" in filters:
            filter_maps.append(Case.module == filters["module"])
        if "level" in filters:
            filter_maps.append(Case.level == filters["level"])
        if "tag" in filters:
            # 支持传入数据为list结构
            tags = filters["tag"]
            if len(tags) == 1:
                filter_maps.append(Case.tag.like("%({tag})%".format(tag=tags[0])))
            else:
                or_filter = list()
                for atag in tags:
                    or_filter.append(Case.tag.like("%({tag})%".format(tag=atag)))
                filter_maps.append(self._or_filter(or_filter))
        if "auto" in filters:
            auto = True if filters["auto"] == "Y" else False
            filter_maps.append(Case.auto == auto)
        if "review" in filters:
            filter_maps.append(Case.review == filters["review"])
        if "creator" in filters:
            filter_maps.append(Case.creator == filters["creator"])
        if "effect" in filters:
            filter_maps.append(Case.effect == filters["effect"])
        try:
            cases = db.session.query(Case.id, Case.name, Case.module, Case.given, Case.when, Case.then, Case.level,
                                     Case.tag, Case.auto, Case.review, Case.result, Case.effect, Case.creator,
                                     Case.create_time, Case.update_time).filter(*filter_maps).all()
            cases = [
                {"id": case[0], "name": case[1], "module": case[2], "given": case[3], "when": case[4], "then": case[5],
                 "level": case[6], "tag": self._tag_db_to_str(case[7]), "auto": "Y" if case[8] else "N",
                 "review": case[9], "result": case[10], "effect": case[11], "creator": case[12],
                 "create_time": case[13], "update_time": case[14]} for case in cases]
        except:
            pass
        return cases

    def add_relationship_card_and_case(self, card_id, case_id):
        relation_id = ""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            relation = CaseRelatedCard()
            relation.case = case_id
            relation.card = card_id
            relation.result = "Created"
            relation.state = "bind"
            relation.create_time = now_time
            relation.update_time = now_time
            relation.operator = None
            db.session.add(relation)
            db.session.flush()
            relation_id = relation.id
            db.session.commit()
            db.session.close()
        except:
            pass
        return relation_id

    def update_relationship_card_and_case(self, card_id, case_id, **args):
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_sql = dict()
        if "state" in args:
            update_sql["state"] = args["state"]
        if "result" in args:
            update_sql["result"] = args["result"]
        update_sql["update_time"] = now_time
        try:
            if not CaseRelatedCard.query.filter(CaseRelatedCard.case==case_id, CaseRelatedCard.card==card_id).count():
                self.add_relationship_card_and_case(card_id, case_id)
            else:
                db.session.query(CaseRelatedCard).filter(CaseRelatedCard.case == case_id,
                                                         CaseRelatedCard.card == card_id).update(update_sql)
        except:
            pass

    def get_case_by_card(self, card_id):
        case_list = list()
        try:
            relation = db.session.query(CaseRelatedCard.case).filter(CaseRelatedCard.card == card_id).all()
            case_list = [case[0] for case in relation]
        except:
            pass
        return case_list

    def get_card_by_case(self, case_id):
        card_list = list()
        try:
            relation = db.session.query(CaseRelatedCard.card).filter(CaseRelatedCard.case == case_id).all()
            card_list = [card[0] for card in relation]
        except Exception as e:
            pass
        return card_list

    def get_bugs(self, **args):
        maps = list()
        if "card_id" in args:
            maps.append(Bug.card == args["card_id"])
        bug_data = db.session.query(Bug.id, Bug.bug, Bug.card, Bug.state, Bug.update_time, Bug.owner, Bug.tester,
                                       Bug.create_time, Bug.level).filter(*maps).all()
        bug_data = [{"id": bug[0], "bug": bug[1], "card": bug[2], "state": bug[3], "update_time": bug[4],
                     "owner": bug[5], "tester": bug[6], "create_time": bug[7], "level": bug[8]} for bug in bug_data]
        return bug_data

    def get_cards(self, **args):
        table_data = list()
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
        elif "id" in args:
            maps.append(Card.id == args["id"])
        maps.append(Card.sprint == Sprint.id)
        result = db.session.query(Card.number, Card.title, Card.point, Card.start_time, Card.state, Sprint.name,
                                  Card.id, Card.type, Card.ac, Card.update_time, Card.original_link). \
            filter(*maps).order_by(Card.update_time.desc()).all()
        for card in result:
            card_data = dict()
            # key: sprint, index, title, point, created_at, state, type, ac, id, dev, qa
            card_data["sprint"] = card[5]
            card_data["index"] = card[0]
            card_data["title"] = card[1]
            card_data["point"] = card[2]
            card_data["start_time"] = card[3]
            card_data["state"] = card[4]
            card_data["type"] = card[7]
            card_data["ac"] = card[8]
            card_data["update_time"] = card[9]
            card_data["original_link"] = card[10]
            card_id = card[6]
            card_data["id"] = card_id
            members = db.session.query(CardMemberRelationship.member, CardMemberRelationship.role).filter(
                CardMemberRelationship.card == card_id).all()
            for member in members:
                if member[1] == "dev":
                    card_data["dev"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
                else:
                    card_data["qa"] = db.session.query(Member.name).filter(Member.id == member[0]).first()[0]
            table_data.append(card_data)
        return table_data

    def update_card(self, index, **args):
        card = Card.query.filter(Card.number == index).first()
        if "state" in args:
            card.state = args["state"]
        if "ac" in args:
            card.ac = args["ac"]
        card.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        db.session.close()

    def add_card(self, **args):
        sprint_id = self.get_sprintID_by_sprintName(args["sprint"])
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        card = Card()
        card.number = args["index"]
        card.title = args["title"]
        card.type = args["type"]
        card.point = args["point"]
        card.ac = args["ac"]
        card.sprint = sprint_id
        card.state = "grooming"
        card.start_time = now_time
        card.update_time = now_time
        db.session.add(card)
        db.session.commit()
        db.session.close()

    def get_card_associated_cards(self, card_id):
        card_id_list = list()
        maps = list()
        # 命中card1
        maps.append(CardRelatedCard.card1 == card_id)
        result = db.session.query(CardRelatedCard.card2).filter(*maps).all()
        card_id_list = [item[0] for item in result]
        # 命中card2
        maps.append(CardRelatedCard.card2 == card_id)
        result = db.session.query(CardRelatedCard.card1).filter(*maps).all()
        card_id_list += [item[0] for item in result]
        return card_id_list

    def add_card_associated_cards(self, **args):
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        crc = CardRelatedCard()
        crc.create_time = now_time
        crc.update_time = now_time
        crc.card1 = args["card1"]
        crc.card2 = args["card2"]
        crc.operator = ""
        db.session.add(crc)
        db.session.commit()
        db.session.close()

    def add_changeLog(self, card_id, prev, current):
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = CardStateChangeLog()
        log.card = card_id
        log.prev = prev
        log.current = current
        log.update_time = now_time
        db.session.add(log)
        db.session.commit()
        db.session.close()

    def get_changeLog(self, card_id):
        logs = db.session.query(CardStateChangeLog.prev, CardStateChangeLog.current, CardStateChangeLog.update_time). \
            filter(CardStateChangeLog.card == card_id).order_by(CardStateChangeLog.update_time.desc()).all()
        logs = [{"prev": log[0], "current": log[1], "update_time": log[2]} for log in logs]
        return logs

    def get_project_members(self, **args):
        maps = list()
        if "name" in args:
            maps.append(Member.name == args["name"])
        elif "active" in args:
            active = args["active"]
            if active == "Active":
                b_active = True
            else:
                b_active = False
            maps.append(Member.active == b_active)
        members = db.session.query(Member.id, Member.name, Member.dev, Member.qa, Member.active, Member.ba,
                                   Member.email, Member.phone).filter(*maps).all()
        member_list = list()
        for member in members:
            member_data = dict()
            member_data["id"] = member[0]
            member_data["name"] = member[1]
            member_data["email"] = member[6]
            member_data["phone"] = member[7]
            if member[2] is True and member[3] is False:
                member_data["role"] = "DEV"
            elif member[2] is False and member[3] is True:
                member_data["role"] = "QA"
            elif member[5] is True:
                member_data["role"] = "BA"
            if member[4] is True:
                member_data["active"] = "Active"
            else:
                member_data["active"] = "Inactive"
            member_list.append(member_data)
        return member_list

    def add_project_member(self, **args):
        member_id = ""
        if "name" in args:
            name = args["name"]
            if not Member.query.filter_by(name=name).count():
                member = Member()
                member.name = name
                if "role" in args:
                    role = args["role"]
                    if role == "DEV":
                        member.dev = True
                        member.qa = False
                        member.ba = False
                    elif role == "QA":
                        member.dev = False
                        member.qa = True
                        member.ba = False
                    elif role == "BA":
                        member.dev = False
                        member.qa = False
                        member.ba = True
                member.active = True
                if "email" in args:
                    member.email = args["email"]
                if "phone" in args:
                    member.phone = args["phone"]
                db.session.add(member)
                db.session.flush()
                member_id = member.id
                db.session.commit()
                db.session.close()
        return member_id

    def update_project_member(self, name, **args):
        update_sql = dict()
        if "role" in args:
            role = args["role"]
            update_sql["dev"] = False
            update_sql["qa"] = False
            update_sql["ba"] = False
            if role == "DEV":
                update_sql["dev"] = True
            elif role == "QA":
                update_sql["qa"] = True
            elif role == "BA":
                update_sql["ba"] = True
        if "email" in args:
            update_sql["email"] = args["email"]
        if "phone" in args:
            update_sql["phone"] = args["phone"]
        if "active" in args:
            if args["active"] == "Active":
                update_sql["active"] = True
            else:
                update_sql["active"] = False
        res = db.session.query(Member).filter(Member.name == name).update(update_sql)
        print("res: ", res)
        db.session.commit()
        db.session.close()

    def add_project(self, **args):
        project_id = ""
        if set(args.keys()).issuperset({"name", "robot"}):
            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                project = Project()
                project.name = args["name"]
                project.robot = args["robot"]
                project.create_at = now_time
                project.points_data = True
                project.cards_data = True
                project.burn_down_chart = True
                project.cumulative_flow_chart = True
                project.point_overflow_rate_data = args["point_overflow_rate_data"]
                project.commitment_fulfillment_rate_data = args["commitment_fulfillment_rate_data"]
                project.good_card_rate_data = args["good_card_rate_data"]
                project.average_test_costs_data = args["average_test_costs_data"]
                project.bug_data = args["bug_data"]
                project.left_bug_data = args["left_bug_data"]
                project.test_coverage_data = args["test_coverage_data"]
                project.regression_test_data = args["regression_test_data"]
                project.points_spent_per_card_chart = args["points_spent_per_card_chart"]
                project.percentage_of_points_delivered_chart = args["percentage_of_points_delivered_chart"]
                project.trend_different_type_cards_chart = args["trend_different_type_cards_chart"]
                project.trend_completion_points_chart = args["trend_completion_points_chart"]
                project.trend_completion_cards_chart = args["trend_completion_cards_chart"]
                project.trend_bug_created_chart = args["trend_bug_created_chart"]
                db.session.add(project)
                db.session.flush()
                project_id = project.id
                db.session.commit()
                db.session.close()
            except Exception as e:
                print(e)
        else:
            print("[func:add_project] 参数不匹配")
        return project_id

    def update_project(self, name, **args):
        try:
            db.session.query(Project).filter(Project.name == name).update(args)
            db.session.commit()
        except Exception as e:
            print("[ERROR] project name: %s update fail (%s)" % (name, e))

    def get_project(self, name):
        project_data = dict()
        try:
            data = db.session.query(Project.name, Project.robot, Project.points_data, Project.cards_data,
                                    Project.burn_down_chart, Project.cumulative_flow_chart,
                                    Project.point_overflow_rate_data,
                                    Project.commitment_fulfillment_rate_data, Project.good_card_rate_data,
                                    Project.average_test_costs_data, Project.bug_data, Project.left_bug_data,
                                    Project.test_coverage_data, Project.regression_test_data,
                                    Project.points_spent_per_card_chart, Project.percentage_of_points_delivered_chart,
                                    Project.trend_different_type_cards_chart, Project.trend_completion_points_chart,
                                    Project.trend_completion_cards_chart, Project.trend_bug_created_chart). \
                filter(Project.name == name).all()[0]
            project_data = {
                "name": data[0],
                "robot": data[1],
                "points_data": data[2],
                "cards_data": data[3],
                "burn_down_chart": data[4],
                "cumulative_flow_chart": data[5],
                "point_overflow_rate_data": data[6],
                "commitment_fulfillment_rate_data": data[7],
                "good_card_rate_data": data[8],
                "average_test_costs_data": data[9],
                "bug_data": data[10],
                "left_bug_data": data[11],
                "test_coverage_data": data[12],
                "regression_test_data": data[13],
                "points_spent_per_card_chart": data[14],
                "percentage_of_points_delivered_chart": data[15],
                "trend_different_type_cards_chart": data[16],
                "trend_completion_points_chart": data[17],
                "trend_completion_cards_chart": data[18],
                "trend_bug_created_chart": data[19],
            }
        except Exception as e:
            print(e)
        return project_data

    def get_project_list(self):
        projects = list()
        try:
            projects = db.session.query(Project.name).order_by(Project.create_at.desc()).all()
        except:
            pass
        projects = [project[0] for project in projects]
        return projects


class WechatMsg:

    def __init__(self):
        self.robot_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f4c26561-1265-4217-9a15-db10aba0efda"

    def send_msg_txt(self, member_list, msg):
        err_msg = ""
        try:
            headers = {"Content-Type": "text/plain"}
            send_data = {
                "msgtype": "text",
                "text": {
                    "content": msg,
                    "mentioned_mobile_list": member_list,
                }
            }
            res = requests.post(url=self.robot_webhook, headers=headers, json=send_data)
            print(res)
        except Exception as e:
            err_msg = e
        return err_msg


class Statistical:
    # 本轮迭代指标：完成点数/完成率，完成卡数/完成率，卡dev/qa/point，成员完成点数，承诺达成率，点溢出率，平均测试点数，平均bug修复时长
    #            良品率，测试覆盖率，产生bug数，遗留bug数
    # 迭代趋势指标：卡类型占比，完成点数，完成卡数，bug数

    def __init__(self, sprint_name):
        self.db_operate = OperateDB()
        self.sprint_data = self._get_sprint_data(sprint_name)
        self.todo_cards, self.done_cards, self.all_cards = self._get_sprint_done_cards_data(sprint_name)

    def _get_sprint_done_cards_data(self, sprint_name):
        done_cards = list()
        todo_cards = list()
        cards = self.db_operate.get_cards(sprint=sprint_name)
        for card in cards:
            # key: sprint, index, title, point, created_at, state, type, ac, id, dev, qa
            if card["state"] == "test done":
                done_cards.append(card)
            else:
                todo_cards.append(card)
        return todo_cards, done_cards, cards

    def _get_sprint_data(self, sprint_name):
        sprint_data = self.db_operate.get_sprint_data(sprint_name=sprint_name)[0]
        return sprint_data

    def _get_dev_members(self):
        return self.db_operate.get_members("dev")

    def _get_card_changelog(self, card_id):
        return self.db_operate.get_changeLog(card_id)

    def _get_card_step_cost_days(self, card_id):
        dev_days = list()
        qa_days = list()
        done_date = 0
        card_log = self.db_operate.get_changeLog(card_id)[::-1]
        for index, log in enumerate(card_log):
            if log["current"] == "in dev":
                end_date = ""
                if index != len(card_log)-1:
                    if card_log[index+1]["prev"] == "in dev":
                        end_date = card_log[index+1]["update_time"].strftime("%Y-%m-%d")
                else:
                    end_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
                    # print("[DEBUG] card_id:", card_id, ", end_date:", end_date)
                if end_date:
                    begin_date = log["update_time"].strftime("%Y-%m-%d")
                    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    dev_days += get_date_list(begin_date, end_date)
            # if log["current"] == "in qa" and index != len(card_log)-1:
            #     if card_log[index+1]["prev"] == "in qa":
            #         begin_date = log["update_time"].strftime("%Y-%m-%d")
            #         end_date = card_log[index+1]["update_time"].strftime("%Y-%m-%d")
            #         begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
            #         end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            #         qa_days += get_date_list(begin_date, end_date)
            if log["current"] == "in qa":
                end_date = ""
                if index != len(card_log)-1:
                    if card_log[index+1]["prev"] == "in qa":
                        end_date = card_log[index+1]["update_time"].strftime("%Y-%m-%d")
                else:
                    end_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
                if end_date:
                    begin_date = log["update_time"].strftime("%Y-%m-%d")
                    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    qa_days += get_date_list(begin_date, end_date)
            if log["current"] == "test done" and index == len(card_log)-1:
                done_date = log["update_time"].strftime("%Y-%m-%d")
                done_date = datetime.datetime.strptime(done_date, "%Y-%m-%d")
        # dev_days = list(set(dev_days) - (set(dev_days) & set(qa_days)))
        # print("card_id:", card_id, ", dev:", dev_days, ", qa:", qa_days)
        return dev_days, qa_days, done_date

    def get_sprint_plan_points(self):
        return self.sprint_data["points"]

    def get_sprint_plan_cards(self):
        return sum([self.sprint_data["story_cards"], self.sprint_data["spike_cards"], self.sprint_data["bug_cards"],
                    self.sprint_data["task_cards"]])

    def get_sprint_done_cards(self):
        return len(self.done_cards)

    def get_sprint_done_points(self):
        return sum([card["point"] for card in self.done_cards])

    def get_sprint_todo_cards(self):
        return len(self.todo_cards)

    def get_sprint_todo_points(self):
        return sum([card["point"] for card in self.todo_cards])

    def get_sprint_card_done_rate(self):
        rate = 0
        if self.get_sprint_plan_cards():
            rate = round(self.get_sprint_done_cards()/self.get_sprint_plan_cards()*100, 2)
        return rate

    def get_sprint_point_done_rate(self):
        rate = 0
        if self.get_sprint_plan_points():
            rate = round(self.get_sprint_done_points()/self.get_sprint_plan_points()*100, 2)
        return rate

    def get_sprint_points_by_day(self):
        # 燃尽图
        start_time = self.sprint_data["start_time"]
        end_time = self.sprint_data["end_time"]
        plan_points = self.sprint_data["points"]
        date_list = get_date_list(start_time, end_time)
        now_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        if now_date in date_list and now_date != date_list[-1]:
            date_list = date_list[:date_list.index(now_date)+1]
        date_points = {}.fromkeys(date_list, 0)
        date_points_list = list()
        for date in date_list:
            exist_cards = [card for card in self.all_cards if datetime_to_date(card["start_time"]) <=
                           datetime.datetime.strptime(date, "%Y-%m-%d")]
            exist_points = sum([card["point"] for card in exist_cards])
            if exist_points < plan_points:
                exist_points = plan_points
            # print("date:", date, "total points:", exist_points)
            done_cards = [card for card in self.all_cards if card["state"] == "test done" and
                          datetime_to_date(card["update_time"]) <= datetime.datetime.strptime(date, "%Y-%m-%d")]
            done_points = sum([card["point"] for card in done_cards])
            # print("date:", date, "done points:", done_points)
            left_points = exist_points - done_points
            date_points[date] = left_points
        date_points_list = [{"date": date[5:], "points": date_points[date]} for date in date_points]
        return date_points_list

    def get_sprint_step_points_by_day(self):
        # 累计流量图
        step_points = list()
        start_time = self.sprint_data["start_time"]
        end_time = self.sprint_data["end_time"]
        date_list = get_date_list(start_time, end_time)
        now_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        if now_date in date_list and now_date != date_list[-1]:
            date_list = date_list[:date_list.index(now_date) + 1]
        step_list = ["grooming", "kick off", "in dev", "desk check", "in qa", "test done"]
        card_dev_step_cost = dict()
        card_qa_step_cost = dict()
        for card in self.all_cards:
            card_dev_step_cost[card["id"]] = self._get_card_step_cost_days(card["id"])[0]
            card_qa_step_cost[card["id"]] = self._get_card_step_cost_days(card["id"])[1]
        dev_pool = list()
        qa_pool = list()
        for date in date_list:
            grooming_cards = sum([1 for card in self.all_cards if datetime_to_date(card["start_time"]) <=
                           datetime.datetime.strptime(date, "%Y-%m-%d")])
            done_cards = sum([1 for card in self.done_cards if self._get_card_step_cost_days(card["id"])[2] <=
                              datetime.datetime.strptime(date, "%Y-%m-%d")])
            qa_pool += [card["index"] for card in self.all_cards if date in card_qa_step_cost[card["id"]]]
            dev_pool += [card["index"] for card in self.all_cards if date in card_dev_step_cost[card["id"]]]
            qa_cards = len(list(set(qa_pool)))
            dev_cards = len(list(set(dev_pool)))
            # print("[INFO] date:", date, ", dev_pool:", list(set(dev_pool)), ", qa_pool:", list(set(qa_pool)))
            # print("[INFO] date:", date, ", groom cards:", grooming_cards, ", dev cards:", dev_cards, ", qa cards:", qa_cards, ", done cards:", done_cards)
            # 注意：这里埋了一个坑，dev time、qa time、done time三个时间不能是同一天，否则累计流图会出现负数的bug
            step_points.append({
                "date": date[5:],
                "value": grooming_cards-dev_cards,
                "step": "Grooming cards"
            })
            step_points.append({
                "date": date[5:],
                "value": dev_cards-qa_cards,
                "step": "In Dev cards"
            })
            step_points.append({
                "date": date[5:],
                "value": qa_cards-done_cards,
                "step": "In QA cards"
            })
            step_points.append({
                "date": date[5:],
                "value": done_cards,
                "step": "Done cards"
            })
        return step_points

    def get_sprint_card_type_num(self):
        story_cards = 0
        spike_cards = 0
        bug_cards = 0
        task_cards = 0
        card_type_num = list()
        for card in self.done_cards:
            if card["type"] == "story":
                story_cards += 1
            if card["type"] == "spike":
                spike_cards += 1
            if card["type"] == "bug":
                bug_cards += 1
            if card["type"] == "task":
                task_cards += 1
        card_type_num.append({
            "type": "story",
            "value": story_cards,
        })
        card_type_num.append({
            "type": "spike",
            "value": spike_cards,
        })
        card_type_num.append({
            "type": "bug",
            "value": bug_cards,
        })
        card_type_num.append({
            "type": "task",
            "value": task_cards,
        })
        return card_type_num

    def get_sprint_points_overflow_rate(self):
        rate = 0
        if self.get_sprint_plan_points():
            rate = round((self.get_sprint_todo_points()+self.get_sprint_done_points())/self.get_sprint_plan_points()*100, 2)
        return rate

    def get_sprint_member_done_point(self):
        members = self._get_dev_members()
        member_points_data = {}.fromkeys(members, 0)
        for card in self.done_cards:
            member_points_data[card["dev"]] += card["point"]
        member_points = [{"type": member, "value": member_points_data[member]} for member in member_points_data]
        return member_points

    def _get_card_bugs(self, card_id):
        total_bugs = 0
        left_bugs = 0
        bugs = self.db_operate.get_bugs(card_id=card_id)
        if bugs:
            for bug in bugs:
                if bug["state"] != "Ignored":
                    total_bugs += 1
                if bug["state"] not in ["Ignored", "Solved"]:
                    left_bugs += 1
        return total_bugs, left_bugs

    def get_sprint_bugs(self):
        bugs = 0
        left_bugs = 0
        good_cards = 0
        good_rate = 0
        if self.all_cards:
            for card in self.all_cards:
                card_id = card["id"]
                card_bugs, card_left_bugs = self._get_card_bugs(card_id)
                bugs += card_bugs
                left_bugs += card_left_bugs
                if card_bugs == 0 and card["state"] == "test done":
                    good_cards += 1
            if self.done_cards:
                good_rate = round(good_cards / len(self.done_cards) * 100, 2)
            else:
                good_rate = 0
        return bugs, left_bugs, good_rate

    def _get_card_step_point(self, card_id):
        card_logs = self._get_card_changelog(card_id)
        dev_time = 0
        qa_time = 0
        for log in card_logs:
            if log["prev"] == "kick off" and log["current"] == "in dev":
                dev_time -= datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "in dev" and log["current"] == "desk check":
                dev_time += datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "desk check" and log["current"] == "in qa":
                qa_time -= datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "in qa" and log["current"] == "test done":
                qa_time += datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "test done" and log["current"] == "in qa":
                qa_time -= datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "in qa" and log["current"] == "desk check":
                qa_time += datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "desk check" and log["current"] == "in dev":
                dev_time -= datetimeStr_switch_int(log["update_time"])
            if log["prev"] == "in dev" and log["current"] == "kick off":
                dev_time += datetimeStr_switch_int(log["update_time"])
        dev_time = deal_with_float(dev_time / (60 * 60 * 24))
        qa_time = deal_with_float(qa_time / (60 * 60 * 24))
        return dev_time, qa_time

    def get_sprint_card_dev_qa_points(self):
        card_points = list()
        for card in self.done_cards:
            card_id = card["id"]
            card_plan_point = card["point"]
            dev_time, qa_time = self._get_card_step_point(card_id)
            card_points.append({
                "index": "%d (%d)" % (card["index"], card_plan_point),
                "Dev": dev_time,
                "QA": qa_time,
            })
        return card_points

    def get_sprint_card_match_points_rate(self):
        rate = 0
        done_cards_num = len(self.done_cards)
        match_point_card_num = 0
        if done_cards_num:
            for card in self.done_cards:
                plan_points = card["point"]
                card_id = card["id"]
                dev_time, qa_time = self._get_card_step_point(card_id)
                if dev_time <= plan_points:
                    match_point_card_num += 1
            rate = round(match_point_card_num/done_cards_num*100, 2)
        return rate

    def get_sprint_average_qa_points(self):
        average_qa_points = 0
        qa_points = 0
        done_cards_num = len(self.done_cards)
        if done_cards_num:
            for card in self.done_cards:
                card_id = card["id"]
                dev_time, qa_time = self._get_card_step_point(card_id)
                qa_points += qa_time
            average_qa_points = round(qa_points/done_cards_num, 2)
        return average_qa_points


def get_date_format(date):
    new_date = re.findall("(\d+\-\d+\-\d+)", date)[0]
    return new_date


def get_random_ids(num):
    id_list = random.sample(range(1000, 9999), num)
    for action_id in id_list:
        yield action_id


def datetimeStr_switch_int(datetime):
    dt_format = "%Y-%m-%d %H:%M:%S"
    ds = datetime.strftime(dt_format)
    dt = time.strptime(ds, dt_format)
    ts = time.mktime(dt)
    return ts


def get_date_list(start_time, end_time):
    date_list = list()
    # start_date = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    # end_date = datetime.datetime.strptime(end_time, "%Y-%m-%d")
    start_date = start_time
    end_date = end_time
    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        start_date += datetime.timedelta(days=1)
    return date_list


def datetime_to_date(dt):
    return datetime.datetime.strptime(dt.strftime("%Y-%m-%d"), "%Y-%m-%d")


def datetime_str_switch_date_datetime(datetime_str):
    date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    date_str = date.strftime("%Y-%m-%d")
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return date


def deal_with_float(num):
    # 保留num的两位小数
    num = round(num, 2)
    integer = num // 1
    point = num * 100 % 100 / 100
    if point < 0.5:
        new_num = integer + 0.5
    else:
        new_num = integer + 1
    return new_num


