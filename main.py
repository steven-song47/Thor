from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from app.models import project_model, monitor_model
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask


# def sensor():
#     """ Function for test purposes. """
#     print("Scheduler is alive!")
#
#
# scheduler = BackgroundScheduler(daemon=True)
# scheduler.add_job(sensor, 'interval', seconds=60)
# scheduler.start()


app = create_app('default')
migrate = Migrate(app, db)


@app.route("/")
def index():
    return "Welcome"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
