from flask import Blueprint
# 等同于demo_main.py中的 app = Flask()
api = Blueprint('api', __name__)

from . import project
from . import chart
from . import case
from . import member
from . import auto
from . import board
from . import dashboard
from . import config