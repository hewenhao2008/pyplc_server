import MySQLdb
import json
import traceback
from flask import Flask, g, request, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

from sae.const import (MYSQL_HOST, MYSQL_HOST_S,
                       MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
                       )

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s:%s/%s' % (
MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_RECORD_QUERIES'] = True

# extensions
db = SQLAlchemy(app)


@app.before_request
def before_request():
    # g.db = SQLAlchemy(app)
    g.db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS,
                          MYSQL_DB, port=int(MYSQL_PORT), charset="utf8")


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'): g.db.close()
        # db2 = getattr(g, 'db2', None)
    if db is not None:
        db.session.remove()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/test')
def test():
    admin = User('admin', 'admin@example.com')
    guest = User('guest', 'guest@example.com')
    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()
    users = User.query.all()
    admin2 = User.query.filter_by(username='admin').first()
    html = "test result:"

    return admin2.username