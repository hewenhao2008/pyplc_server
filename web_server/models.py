# coding=utf-8
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from sqlalchemy.orm import class_mapper

from ext import db

engine = db.create_engine('mysql://yakumo17s:touhouproject@114.67.225.15:3306/pyplc')

def check_int(column):
    if column:
        return int(column)
    else:
        return column


def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)


roles = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


class VarQueries(db.Model):
    __tablename__ = 'variables_queries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query_group.id'))
    variable_id = db.Column(db.Integer, db.ForeignKey('yjvariableinfo.id'))
    query = db.relationship('QueryGroup', back_populates='variables')
    variable = db.relationship('YjVariableInfo', back_populates='queries')


class VarGroups(db.Model):
    __tablename__ = 'variables_groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_id = db.Column(db.Integer, db.ForeignKey('yjvariableinfo.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('yjgroupinfo.id'))
    variable = db.relationship('YjVariableInfo', back_populates='groups')
    group = db.relationship('YjGroupInfo', back_populates='variables')


class YjStationInfo(db.Model):
    __tablename__ = 'yjstationinfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_name = db.Column(db.String(30))
    mac = db.Column(db.String(20))
    ip = db.Column(db.String(20))
    note = db.Column(db.String(200))
    id_num = db.Column(db.String(200))
    plc_count = db.Column(db.Integer)
    ten_id = db.Column(db.String(255))
    item_id = db.Column(db.String(20))
    con_time = db.Column(db.Integer)
    is_modify = db.Column(db.Boolean)
    phone = db.Column(db.BigInteger)

    plcs = db.relationship('YjPLCInfo', backref='yjstationinfo', lazy='dynamic',
                           cascade="delete, delete-orphan")

    logs = db.relationship('TransferLog', backref='yjstationinfo', lazy='dynamic', cascade="delete, delete-orphan")

    sms = db.relationship('SMSPhone', backref='yjstationinfo', lazy='dynamic', cascade="delete, delete-orphan")

    voice = db.relationship('VoiceCall', backref='yjstationinfo', lazy='dynamic', cascade="delete, delete-orphan")

    infos = db.relationship('TerminalInfo', backref='yjstationinfo', lazy='dynamic', cascade="delete, delete-orphan")

    def __repr__(self):
        return '<Station : ID(%r) Name(%r) >'.format(self.id, self.station_name)


class YjPLCInfo(db.Model):
    __tablename__ = 'yjplcinfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plc_name = db.Column(db.String(30))
    note = db.Column(db.String(200))
    ip = db.Column(db.String(30))
    mpi = db.Column(db.Integer)
    type = db.Column(db.Integer)
    plc_type = db.Column(db.Integer)
    ten_id = db.Column(db.String(255))
    item_id = db.Column(db.String(20))

    rack = db.Column(db.Integer)
    slot = db.Column(db.Integer)
    tcp_port = db.Column(db.Integer)

    station_id = db.Column(db.Integer, db.ForeignKey('yjstationinfo.id'))

    groups = db.relationship('YjGroupInfo', backref='yjplcinfo', lazy='dynamic',
                             cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<PLC : ID(%r) Name(%r) >'.format(self.id, self.plc_name)


class YjGroupInfo(db.Model):
    __tablename__ = 'yjgroupinfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(20))
    note = db.Column(db.String(100))
    is_upload = db.Column(db.Boolean)
    upload_cycle = db.Column(db.Integer)
    ten_id = db.Column(db.String(255))
    item_id = db.Column(db.String(20))
    acquisition_cycle = db.Column(db.Integer)
    server_record_cycle = db.Column(db.Integer)
    group_type = db.Column(db.Integer)

    plc_id = db.Column(db.Integer, db.ForeignKey('yjplcinfo.id'))

    variables = db.relationship('VarGroups', back_populates='group')

    def __repr__(self):
        return '<Group :ID(%r) Name(%r) >'.format(self.id, self.group_name)


class YjVariableInfo(db.Model):
    __tablename__ = 'yjvariableinfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_name = db.Column(db.String(20))
    db_num = db.Column(db.Integer)
    address = db.Column(db.Float)
    data_type = db.Column(db.Integer)
    rw_type = db.Column(db.Integer)
    note = db.Column(db.String(50))
    ten_id = db.Column(db.String(200))
    item_id = db.Column(db.String(20))
    write_value = db.Column(db.Integer)
    area = db.Column(db.Integer)
    is_analog = db.Column(db.Boolean)
    analog_low_range = db.Column(db.Float)
    analog_high_range = db.Column(db.Float)
    digital_low_range = db.Column(db.Float)
    digital_high_range = db.Column(db.Float)
    offset = db.Column(db.Float)

    values = db.relationship('Value', backref='yjvariableinfo', lazy='dynamic', cascade="delete, delete-orphan")
    alarms = db.relationship('VarAlarmInfo', backref='yjvariableinfo', lazy='dynamic', cascade="delete, delete-orphan")
    params = db.relationship('Parameter', backref='yjvariableinfo', lazy='dynamic', cascade="delete, delete-orphan")

    groups = db.relationship('VarGroups', back_populates='variable')
    queries = db.relationship('VarQueries', back_populates='variable')

    def __repr__(self):
        return '<Variable :ID(%r) Name(%r) >'.format(self.id, self.variable_name)


class Value(db.Model):
    __tablename__ = 'values'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_id = db.Column(db.BigInteger, db.ForeignKey('yjvariableinfo.id'))
    value = db.Column(db.Float)
    time = db.Column(db.Integer)

    def __repr__(self):
        return '<Value {} {} {} {}'.format(self.id, self.variable_id, self.value, self.time)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32))
    pw_hash = db.Column(db.String(128))
    login_count = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(64), default='unknown')
    last_login_time = db.Column(db.Integer)

    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('user', lazy='dynamic'),
        passive_deletes=True
    )

    def __init__(self, username, password, email=None):
        self.username = username
        # self.set_password(password)
        self.pw_hash = password
        self.email = email

    def __repr__(self):
        return '<User {}'.format(self.username)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except TypeError:
            return None
        user_id = data['id']
        user = User.query.get(user_id)

        try:
            assert (data['time'] == user.last_login_time)
        except AssertionError:
            return None

        return user

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return unicode(self.id)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        # return check_password_hash(self.pw_hash, password)
        return self.pw_hash == password


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True)
    description = db.Column(db.String(64))

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class TransferLog(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(db.Integer, db.ForeignKey('yjstationinfo.id'))
    level = db.Column(db.Integer)
    time = db.Column(db.Integer)
    note = db.Column(db.String(200))


class QueryGroup(db.Model):
    __tablename__ = 'query_group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))

    variables = db.relationship('VarQueries', back_populates='query')


class VarAlarm(db.Model):
    __tablename__ = 'var_alarm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alarm_id = db.Column(db.Integer, db.ForeignKey('var_alarm_info.id'))
    time = db.Column(db.Integer)


class VarAlarmLog(db.Model):
    __tablename__ = 'var_alarm_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alarm_id = db.Column(db.Integer, db.ForeignKey('var_alarm_info.id'))
    time = db.Column(db.Integer)
    status = db.Column(db.Integer)


class VarAlarmInfo(db.Model):
    __tablename__ = 'var_alarm_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_id = db.Column(db.Integer, db.ForeignKey('yjvariableinfo.id'))
    alarm_type = db.Column(db.Integer)
    note = db.Column(db.String(128))
    is_send_message = db.Column(db.Boolean)
    type = db.Column(db.Integer)  # 1 bool 2 判断数值
    symbol = db.Column(db.Integer)  # 1 > 2 >= 3 < 4 <= 5 ==
    limit = db.Column(db.Float)
    delay = db.Column(db.Integer)

    logs = db.relationship('VarAlarmLog', backref='var_alarm_info', lazy='dynamic', cascade="delete, delete-orphan")
    alarms = db.relationship('VarAlarm', backref='var_alarm_info', lazy='dynamic', cascade="delete, delete-orphan")


class InterfaceLog(db.Model):
    __tablename__ = 'interface_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32))
    host_url = db.Column(db.String(32))
    method = db.Column(db.String(8))
    time = db.Column(db.Integer)
    param = db.Column(db.Text)
    old_data = db.Column(db.Text)
    new_data_id = db.Column(db.Integer)
    endpoint = db.Column(db.String(32))


class Parameter(db.Model):
    __tablename__ = 'parameter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_id = db.Column(db.Integer, db.ForeignKey('yjvariableinfo.id'))
    param_name = db.Column(db.String(32))
    unit = db.Column(db.String(16))


class StationAlarm(db.Model):
    __tablename__ = 'station_alarm'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_num = db.Column(db.String(200))
    code = db.Column(db.Integer)
    note = db.Column(db.Text)
    time = db.Column(db.Integer)


class PLCAlarm(db.Model):
    __tablename__ = 'plc_alarm'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_num = db.Column(db.String(200))
    plc_id = db.Column(db.Integer)
    note = db.Column(db.Text)
    time = db.Column(db.Integer)
    code = db.Column(db.Integer)


class SMSPhone(db.Model):
    __tablename__ = 'sms_phone'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(db.Integer, db.ForeignKey('yjstationinfo.id'))
    number = db.Column(db.BigInteger)
    level = db.Column(db.Integer)


class VoiceCall(db.Model):
    __tablename__ = 'voice_call'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(db.Integer, db.ForeignKey('yjstationinfo.id'))
    number = db.Column(db.BigInteger)
    level = db.Column(db.Integer)


class TerminalInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boot_time = db.Column(db.Integer)
    total_usage = db.Column(db.Integer)
    free_usage = db.Column(db.Integer)
    usage_percent = db.Column(db.Float)
    total_memory = db.Column(db.Integer)
    free_memory = db.Column(db.Integer)
    memory_percent = db.Column(db.Float)
    bytes_sent = db.Column(db.Integer)
    bytes_recv = db.Column(db.Integer)
    cpu_percent = db.Column(db.Float)

    station_id = db.Column(db.Integer, db.ForeignKey('yjstationinfo.id'))
