import pymysql

from flask import current_app


class ConnMySQL(object):
    def __init__(self):
        self.db = pymysql.connect(
            host=current_app.config['HOSTNAME'],
            port=3306,
            user=current_app.config['USERNAME'],
            passwd=current_app.config['PASSWORD'],
            db=current_app.config['DATABASE'],
            charset='utf8'
        )

    def __enter__(self):
        return self.db

    def __exit__(self, *args):
        self.db.close()
