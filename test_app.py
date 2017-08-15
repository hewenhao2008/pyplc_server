import flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sae.const

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://1m4zwn31kn:i155mii155xx51xkyi0ximxl3hzy3hzk244lk4j0@w.rdc.sae.sina.com.cn:3306/app_yakumo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32))
    pw_hash = db.Column(db.String(128))
    login_count = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(64), default='unknown')
    last_login_time = db.Column(db.Integer)


# db.create_all()


@app.route("/")
def hello():
    logging.warn('2')

    import MySQLdb

    db = MySQLdb.connect(host='w.rdc.sae.sina.com.cn',user='1m4zwn31kn', passwd='i155mii155xx51xkyi0ximxl3hzy3hzk244lk4j0', db='app_yakumo', port=3306 )

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s' \
    #                           % (sae.const.MYSQL_USER, sae.const.MYSQL_PASS,
    #                              sae.const.MYSQL_HOST, int(sae.const.MYSQL_PORT), sae.const.MYSQL_DB)
    cursor = db.cursor()


    cursor.execute('select * from user')
    #
    result = cursor.fetchone()
    db.close()
    import random

    a = User.query.first()
    print a.id, a.name
    # a = Test(id=1, name='1')
    # # print a.__init__(), a.__getattribute__(1)
    #
    # db.session.add(a)
    #
    # db.session.commit()
    print result
    # return 'a'
    return 'a'