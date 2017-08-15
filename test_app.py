import flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://x5wwm4m152:lm40k0yihh33z4j2wzzmlxkkj3iz01mhzwmw5y2k@w.rdc.sae.sina.com.cn:3306/app_pasa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))


# db.create_all()


@app.route("/")
def hello():
    logging.warn('2')

    import random

    a = Test(id=1, name='1')
    # print a.__init__(), a.__getattribute__(1)

    db.session.add(a)

    db.session.commit()

    return a.id