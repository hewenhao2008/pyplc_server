import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://1m4zwn31kn:i155mii155xx51xkyi0ximxl3hzy3hzk244lk4j0@w.rdc.sae.sina.com.cn:3306/app_yakumo'
db = SQLAlchemy(app)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))


db.create_all()


@app.route("/")
def hello():
    import random
    a = Test('{}'.format(random.randint(1, 10)))
    db.session.add(a)
    db.session.commit()
    return a.id
