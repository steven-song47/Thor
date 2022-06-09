from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from app.models import project_model

app = create_app('default')
migrate = Migrate(app, db)


@app.route("/")
def index():
    return "Welcome"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
