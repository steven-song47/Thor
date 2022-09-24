from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os


# MySQL配置
mysql_info = dict(
    host='127.0.0.1',
    port=3306,
    dbname='project_management',
    username='root',
    password='s0095296..'
)

'''
    // setInterval( function () {
    //   t.ajax.reload(); // 刷新表格数据，分页信息不会重置
    // }, 5000 );
'''
# MYSQL_URL = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (mysql_info['username'], mysql_info['password'],
#                                                            mysql_info['host'], mysql_info['port'], mysql_info['dbname'])
MYSQL_URL = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql://root:s0095296..@127.0.0.1:3306/project_management'


# apscheduler 配置
class TaskConfig(object):

    JOBS = [ ]
    SCHEDULER_JOBSTORES = {
        # 'default': SQLAlchemyJobStore(url=MYSQL_URL)
    }
    SCHEDULER_EXECUTORS = {
        # 'default': {'type': 'threadpool', 'max_workers': 20}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 5
    }
    SCHEDULER_API_ENABLED = False
    # 设置时区
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SECRET_KEY = "random string"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = MYSQL_URL

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging import FileHandler
        logging.basicConfig(level=logging.INFO)
        file_handler = FileHandler("info.log")
        # file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or ''
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = MYSQL_URL

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging import FileHandler
        logging.basicConfig(level=logging.INFO)
        file_handler = FileHandler("info.log")
        # file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}