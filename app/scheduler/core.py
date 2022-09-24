from .. import db, scheduler
from .tasks import monitor_api_task
from flask import current_app


def job_from_parm(task_name, **jobargs):
    id = jobargs['id']
    func = __name__ + ":" + task_name
    args = jobargs['cmd']
    trigger_type = jobargs['trigger_type']

    if trigger_type == "date":
        # run_date = date(2022,9,22) or "2022-09-22 12:00:00"
        run_date = jobargs['run_date']
        current_app.apscheduler.scheduler.add_job(func=func, id=id, kwargs={'cmd': args, 'task_id': id}, trigger='date',
                                                  run_date=run_date)
        print("添加一次性任务成功---[ %s ] " % id)
        return id

    elif trigger_type == "interval":
        time_value = dict()
        if jobargs["unit"] == "seconds":
            time_value["seconds"] = jobargs["value"]
        elif jobargs["unit"] == "minutes":
            time_value["minutes"] = jobargs["value"]
        elif jobargs["unit"] == "hours":
            time_value["hours"] = jobargs["value"]
        elif jobargs["unit"] == "days":
            time_value["days"] = jobargs["value"]
        elif jobargs["unit"] == "weeks":
            time_value["weeks"] = jobargs["value"]
        current_app.apscheduler.scheduler.add_job(func=func, id=id, kwargs={'cmd': args, 'task_id': id},
                                                  trigger='interval', **time_value, replace_existing=True)
        print("添加时间间隔执行任务成功任务成功---[ %s ] " % id)
        return id

    elif trigger_type == "cron":
        value = jobargs["value"]
        time_value = dict()
        if "second" in value:
            time_value["second"] = value["value"]
        if "minute" in value:
            time_value["minute"] = value["minute"]
        if "hour" in value:
            time_value["hour"] = value["hour"]
        if "day_of_week" in value:
            time_value["day_of_week"] = value["day_of_week"]
        if "day" in value:
            time_value["day"] = value["day"]
        if "week" in value:
            time_value["week"] = value["week"]
        if "month" in value:
            time_value["month"] = value["month"]
        if "year" in value:
            time_value["year"] = value["year"]
        current_app.apscheduler.scheduler.add_job(func=func, id=id, kwargs={'cmd': args, 'task_id': id}, trigger='cron',
                                                  **time_value, replace_existing=True)
        print("添加周期执行任务成功任务成功---[ %s ] " % id)
        return id
    else:
        pass


def pause_by_job_id(job_id):
    current_app.apscheduler.scheduler.pause_job(job_id)
    print("定时任务暂停成功---[ %s ] " % job_id)
