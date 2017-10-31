from flask import Blueprint
from os import path

from web_server.ext import Api
from web_server.rest.api_alarm import AlarmResource
from web_server.rest.api_alarm_info import AlarmInfoResource
from web_server.rest.api_alarm_log import AlarmLogResource
from web_server.rest.api_group import GroupResource
from web_server.rest.api_interface_log import InterfaceLogResource
from web_server.rest.api_param import ParameterResource
from web_server.rest.api_plc import PLCResource
from web_server.rest.api_plc_alarm import PLCAlarmResource
from web_server.rest.api_query import QueryResource
from web_server.rest.api_station import StationResource
from web_server.rest.api_station_alarm import StationAlarmResource
from web_server.rest.api_station_status import StatusResource
from web_server.rest.api_user import UserResource
from web_server.rest.api_value import ValueResource
from web_server.rest.api_variable import VariableResource
from web_server.rest.auth import AuthApi

api_blueprint = Blueprint(
    'api',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'api'),
    url_prefix='/api'
)

api = Api(api_blueprint)
api.add_resource(AuthApi, '/auth')
api.add_resource(StationResource, '/station', endpoint='yjstationinfo')
api.add_resource(PLCResource, '/plc', endpoint='yjplcinfo')
api.add_resource(GroupResource, '/group', endpoint='yjgroupinfo')
api.add_resource(VariableResource, '/variable', endpoint='yjvariableinfo')
api.add_resource(ValueResource, '/value', endpoint='value')
api.add_resource(StatusResource, '/status', endpoint='transferlog')
api.add_resource(QueryResource, '/query', endpoint='querygroup')
api.add_resource(AlarmInfoResource, '/alarm_info', endpoint='varalarminfo')
api.add_resource(AlarmLogResource, '/alarm_log', endpoint='varalarmlog')
api.add_resource(AlarmResource, '/alarm', endpoint='varalarm')
api.add_resource(UserResource, '/user', endpoint='user')
api.add_resource(InterfaceLogResource, '/interface_log', endpoint='interfacelog')
api.add_resource(ParameterResource, '/param', endpoint='parameter')
api.add_resource(StationAlarmResource, '/station_alarm')
api.add_resource(PLCAlarmResource, '/plc_alarm')
