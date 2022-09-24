from flask import Flask
from flask_apscheduler import APScheduler


class Config:
    # JOBS = [
    #     {
    #         "id": "job1",
    #         "func": "scheduler:add",
    #         "args": (1, 2),
    #         "trigger": "interval",
    #         "seconds": 10,
    #     }
    # ]

    SCHEDULER_API_ENABLED = True


def add(a, b):
    print(a+b)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(port=5001)