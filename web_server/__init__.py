# coding=utf-8

from celery import Celery
from flask import Flask, request, session
from flask import request_tearing_down
from flask_login import user_logged_in,  current_user

from models import *
from ext import mako, hashing, api, admin, login_manager, csrf, cache, debug_toolbar, CSRFProtect
from forms import RegistrationForm, LoginForm
from config import DevConfig, ProdConfig

from web_server.rest.api_plc import PLCResource
from web_server.rest.api_station import StationResource
from web_server.rest.api_group import GroupResource
from web_server.rest.api_variable import VariableResource
from web_server.rest.api_value import ValueResource
from web_server.rest.auth import AuthApi


from web_server.controllers.basic import basic_blueprint
from web_server.controllers.api import api_blueprint
from web_server.controllers.client import client_blueprint

# 设置默认编码
# 不用这段会使得jinja渲染flash消息时产生编码错误
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def create_app(config_name):
    app = Flask(__name__, template_folder='templates')

    # here = os.path.abspath(os.path.dirname(__file__))

    # if os.path.exists('dev'):
    #     app.config.from_object(DevConfig)
    # else:
    app.config.from_object(ProdConfig)

    # eventlet.monkey_patch()
    mako.init_app(app)
    db.init_app(app)
    # with app.app_context():
    #     db.create_all()
    hashing.init_app(app)
    # admin.init_app(app)
    login_manager.init_app(app)
    # csrf.init_app(app)
    debug_toolbar.init_app(app)
    # cache.init_app(app)

    # SOCKETIO_REDIS_URL = app.config['CELERY_BACKEND_URL']
    # socketio.init_app(
    #     app, async_mode='eventlet',
    #     message_queue=SOCKETIO_REDIS_URL
    # )

    # celery = Celery(app.name)
    # celery.conf.update(app.config)

    api.init_app(app)

    admin.add_view(CustomView(name='Custom'))
    show_models = [YjStationInfo, YjPLCInfo, YjGroupInfo, YjVariableInfo, Value, TransferLog, User]

    for model in show_models:
        admin.add_view(
            CustomModelView(model, db.session,
                            category='models')
        )
    admin.add_view(CustomFileAdmin(os.path.join(os.path.dirname(__file__), 'static'),
                                   '/static/',
                                   name='Static File'))

    def value2dict(std):
        return {
            "id": std.id,
            "variable_id": std.variable_id,
            "value": std.value
        }

    def get_current_user():
        return session['username']

    @app.errorhandler(500)
    def server_inner_error(error):
        return u"内部代码错误 by yakumo17s"

    def close_db_connection(sender, **extra):
        db.session.close()
        # sender.logger.debug('Database close.')

    request_tearing_down.connect(close_db_connection, app)

    # @app.before_first_request
    # def set_up():


    @app.context_processor
    def template_extras():
        return {'enumerate': enumerate, 'current_user': current_user}

    @app.template_filter('capitalize')
    def reverse_filter(s):
        return s.capitalize()

    @user_logged_in.connect_via(app)
    def _track_logins(sender, user, **extra):
        # 记录用户登录次数，登录IP
        user.login_count += 1
        user.last_login_ip = request.remote_addr
        user.last_login_time = int(time.time())
        db.session.add(user)
        db.session.commit()

    @login_manager.user_loader
    def user_loader(user_id):
        user = User.query.get(user_id)
        return user

    # def _get_frame(date_string):
    #     db = MySQLdb.connect('localhost', 'web', 'web', 'pyplc')
    #     query = 'SELECT * FROM {}'.format(date_string)
    #     df = read_sql(query, db)
    #     df = df.head(100)
    #     return df
    #
    # @app.route('/db/<any(yjstationinfo, yjplcinfo, yjgroupinfo, yjvariableinfo):date_string>/')
    # @cache.cached(timeout=10)
    # def show_tables(date_string=None):
    #     df = _get_frame(date_string)
    #     if isinstance(df, bool) and not df:
    #         return 'Bad data format!'
    #     return render_template('show_data.html', df=df.to_html(classes='frame'), date_string=date_string)

    app.register_blueprint(basic_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(client_blueprint)
    return app
