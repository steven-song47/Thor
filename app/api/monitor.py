from . import api
from flask import jsonify, request, flash
from ..models.project_model import *
from .. import db, scheduler
from .support.project_management import *
from ..scheduler.core import job_from_parm, pause_by_job_id


@api.route("/monitor/createJob", methods=["POST"])
def create_job():
    response = {'status': '-1'}
    job_id = ""
    # date job
    if request.json["trigger_type"] == "date":
        data = {
            "id": request.json["id"],
            "cmd": request.json["cmd"],
            "trigger_type": "date",
            "run_date": request.json["run_date"],
        }
        try:
            job_id = job_from_parm("monitor_api_task", **data)
        except Exception as e:
            response['msg'] = str(e)
            print(e)

    # interval job
    if request.json["trigger_type"] == "interval":
        data = {
            "id": request.json["id"],
            "cmd": request.json["cmd"],
            "trigger_type": "interval",
            "unit": request.json["unit"],
            "value": request.json["value"],
        }

        response = {'status': '-1'}
        try:
            job_id = job_from_parm("monitor_api_task", **data)
        except Exception as e:
            response['msg'] = str(e)
            print(e)

    # cron job
    if request.json["trigger_type"] == "cron":
        data = {
            "id": request.json["id"],
            "cmd": request.json["cmd"],
            "trigger_type": "cron",
            "value": request.json,
        }
        response = {'status': '-1'}
        try:
            job_id = job_from_parm("monitor_api_task", **data)
        except Exception as e:
            response['msg'] = str(e)
            print(e)

    return jsonify({"code": 200, "success": True, "job_id": job_id})


@api.route("/monitor/pauseJob", methods=["POST"])
def pause_job():
    data = request.get_json(force=True)
    print(data)
    job_id = data.get("id")
    pause_by_job_id(job_id)
    return jsonify({"code": 200, "success": True, "job_id": job_id})
