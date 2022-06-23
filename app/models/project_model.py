# coding=utf-8
from .. import db


class Card(db.Model):
    __tablename__ = "card"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer)
    point = db.Column(db.Integer)
    type = db.Column(db.String(50))
    title = db.Column(db.Text)
    ac = db.Column(db.Text)
    start_time = db.Column(db.Date)
    state = db.Column(db.String(50))
    sprint = db.Column(db.Integer, db.ForeignKey("sprint.id"))
    update_time = db.Column(db.DateTime)
    operator = db.Column(db.String(50))
    # case = db.relationship("Case", backref="card_case")
    task = db.relationship("Task", backref="card_task")
    bug = db.relationship("Bug", backref="card_bug")
    risk = db.relationship("Risk", backref="card_risk")
    membership = db.relationship("CardMemberRelationship", backref="card_membership")
    changelog = db.relationship("CardStateChangeLog", backref="card_changelog")
    relatedCase = db.relationship("CaseRelatedCard", backref="card_relatedCase")


class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)
    ba = db.Column(db.Boolean)
    dev = db.Column(db.Boolean)
    qa = db.Column(db.Boolean)
    active = db.Column(db.Boolean)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    cardship = db.relationship("CardMemberRelationship", backref="member_cardship")


class CardMemberRelationship(db.Model):
    __tablename__ = "cardMemberRelationship"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    member = db.Column(db.Integer, db.ForeignKey("member.id"))
    role = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class Sprint(db.Model):
    __tablename__ = "sprint"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    card = db.relationship("Card", backref="card_sprint")
    start_time = db.Column(db.Date)
    end_time = db.Column(db.Date)
    point = db.Column(db.Integer)
    remark = db.Column(db.String(100))
    story_cards = db.Column(db.Integer)
    spike_cards = db.Column(db.Integer)
    bug_cards = db.Column(db.Integer)
    task_cards = db.Column(db.Integer)


class Case(db.Model):
    __tablename__ = "case"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    module = db.Column(db.String(100))
    review = db.Column(db.String(50))
    given = db.Column(db.String(500))
    when = db.Column(db.String(500))
    then = db.Column(db.String(500))
    level = db.Column(db.Integer)
    tag = db.Column(db.String(50))
    auto = db.Column(db.Boolean)
    effect = db.Column(db.String(50))
    result = db.Column(db.String(50))
    creator = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    relatedCard = db.relationship("CaseRelatedCard", backref="case_relatedCard")


class CaseRelatedCard(db.Model):
    __tablename__ = "caseRelatedCard"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case = db.Column(db.Integer, db.ForeignKey("case.id"))
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    result = db.Column(db.String(50))
    operator = db.Column(db.String(50))
    state = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class Bug(db.Model):
    __tablename__ = "bug"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bug = db.Column(db.String(500))
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    state = db.Column(db.String(50))
    level = db.Column(db.String(50))
    owner = db.Column(db.String(50))
    tester = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(500))
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    state = db.Column(db.String(50))
    owner = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class Risk(db.Model):
    __tablename__ = "risk"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    risk = db.Column(db.String(500))
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    state = db.Column(db.String(50))
    level = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class CardStateChangeLog(db.Model):
    __tablename__ = "cardStateChangeLog"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card = db.Column(db.Integer, db.ForeignKey("card.id"))
    prev = db.Column(db.String(50))
    current = db.Column(db.String(50))
    update_time = db.Column(db.DateTime)
    operator = db.Column(db.String(50))


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    robot = db.Column(db.String(500))
    create_at = db.Column(db.DateTime)
    points_data = db.Column(db.Boolean)
    cards_data = db.Column(db.Boolean)
    burn_down_chart = db.Column(db.Boolean)
    cumulative_flow_chart = db.Column(db.Boolean)
    point_overflow_rate_data = db.Column(db.Boolean)
    commitment_fulfillment_rate_data = db.Column(db.Boolean)
    good_card_rate_data = db.Column(db.Boolean)
    average_test_costs_data = db.Column(db.Boolean)
    bug_data = db.Column(db.Boolean)
    left_bug_data = db.Column(db.Boolean)
    test_coverage_data = db.Column(db.Boolean)
    regression_test_data = db.Column(db.Boolean)
    points_spent_per_card_chart = db.Column(db.Boolean)
    percentage_of_points_delivered_chart = db.Column(db.Boolean)
    trend_different_type_cards_chart = db.Column(db.Boolean)
    trend_completion_points_chart = db.Column(db.Boolean)
    trend_completion_cards_chart = db.Column(db.Boolean)
    trend_bug_created_chart = db.Column(db.Boolean)

