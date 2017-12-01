# coding=utf-8

from os import path
import time
from flask import Blueprint, request, jsonify

# from mc import mc
from web_server.ext import db
from web_server.models import (YjStationInfo, Value, VarAlarmInfo, VarAlarmLog, StationAlarm, PLCAlarm, VarAlarm)
from web_server.util import encryption_server, decryption_server
from web_server.utils.aliyun_sms import sms_alarm
from web_server.utils.response import make_response
from web_server.utils.client_data import config_data

client_blueprint = Blueprint(
    'client',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'client'),
    url_prefix='/client'
)


def get_alarm(v, station, message_count):
    # 获取历史报警
    last_log = VarAlarmLog.query.join(VarAlarmInfo, VarAlarmInfo.variable_id == v['variable_id']). \
        filter(VarAlarmLog.alarm_id == VarAlarmInfo.id).order_by(VarAlarmLog.time.desc()).first()
    status = v['is_alarm']

    # 历史报警不存在，写入历史报警和当前报警
    print('status', status, last_log)
    if last_log is None:
        alarm_info = VarAlarmInfo.query.filter_by(variable_id=v['variable_id']).first()
        if status == 1:
            log = VarAlarmLog(
                alarm_id=alarm_info.id,
                time=v['time'],
                status=status
            )
            db.session.add(log)

            alarm = VarAlarm(
                alarm_id=alarm_info.id,
                time=v['time']
            )
            db.session.add(alarm)

            # 发送短信
            if alarm_info.is_send_message and station.phone and station.station_name:
                print('发送短信')
                if message_count > 0:
                    sms_alarm(station.phone, {'name': str(station.station_name)})
                    message_count -= 1
    else:
        # 历史报警存在，检查状态。相同不做处理，不相同时，记录本次状态。同时增加或删除当前报警表内该变量信息。
        print(last_log.status != status)
        if last_log.status != status:
            log = VarAlarmLog(
                alarm_id=last_log.alarm_id,
                time=v['time'],
                status=status
            )
            db.session.add(log)
            print(status, type(status))
            if status == 1:
                print(1)
                alarm = VarAlarm(
                    alarm_id=last_log.alarm_id,
                    time=v['time']
                )
                db.session.add(alarm)
                # 发送短信
                alarm_info = VarAlarmInfo.query.filter_by(id=last_log.alarm_id).first()
                print(alarm_info)
                print(alarm_info.is_send_message, station.phone, station.station_name)
                if alarm_info.is_send_message and station.phone and station.station_name:
                    print('发短信2')
                    if message_count > 0:
                        sms_alarm(station.phone, {'name': str(station.station_name)})
                        message_count -= 1
            elif status == 0:
                print(0)
                alarm = VarAlarm.query.filter(VarAlarm.alarm_id == last_log.alarm_id).first()
                if alarm:
                    db.session.delete(alarm)


@client_blueprint.route('/beats', methods=['POST'])
def beats():
    # 设置每次上传时最大发送的短信条数
    message_count = 1

    # 获取心跳数据
    rv = request.get_data()
    # data = rv
    data = decryption_server(rv)

    # 根据id_num查询终端数据模型
    station = YjStationInfo.query.filter_by(id_num=data['id_num']).first()

    if station:
        # 记录连接时间
        station.con_time = int(time.time())

        db.session.add(station)

        # 记录变量报警信息
        if data['data_alarms']:
            for log in data['data_alarms']:
                get_alarm(station, log, message_count)

            print('记录变量报警完成')

        # 记录终端故障信息
        if data['station_alarms']:
            for station_alarm in data['station_alarms']:
                alarm = StationAlarm(
                    id_num=station_alarm['id_num'],
                    code=station_alarm['code'],
                    note=station_alarm['note'],
                    time=station_alarm['time']
                )
                db.session.add(alarm)
        print('记录终端故障完成')

        # 记录PLC故障信息
        if data['plc_alarms']:
            for plc_alarm in data['plc_alarms']:
                alarm = PLCAlarm(
                    id_num=plc_alarm['id_num'],
                    plc_id=plc_alarm['plc_id'],
                    level=plc_alarm['level'],
                    note=plc_alarm['note'],
                    time=plc_alarm['time'],
                    code=plc_alarm['code']
                )
                db.session.add(alarm)
        print('记录PLC故障完成')

        modification = station.is_modify
        status = 'ok'

        # data = encryption(data)

    else:
        modification = 0
        status = 'error'

    print('心跳记录完成，返回确认信息')

    # 返回信息
    data = {
        'is_modify': modification,
        'status': status
    }
    db.session.commit()

    return jsonify(data)


@client_blueprint.route('/config', methods=['POST'])
def set_config():
    if request.method == 'POST':
        data = request.get_json(force=True)

        station = db.session.query(YjStationInfo).filter_by(id_num=data['id_num']).first()

        if not station:
            response = make_response(
                'error',
                400,
                msg='站点信息不存在'
            )
            return response

        data = config_data(station)

        # 加密
        data = encryption_server(data)

        response = make_response('OK', 200, data=data)
        return response


@client_blueprint.route('/confirm/config', methods=['POST'])
def confirm_config():
    if request.method == 'POST':
        data = request.get_json()

        station = db.session.query(YjStationInfo).filter_by(id_num=data['id_num']).first()

        # 将本次发送过配置的站点数据表设置为无更新
        station.modification = 0

        db.session.add(station)
        db.session.commit()

        response = make_response('OK', 200, data=data)

        return response


@client_blueprint.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        data = request.get_data()
        data = decryption_server(data)

        # 验证上传数据
        id_num = data['id_num']

        # 查询服务器是否有正在上传的站信息
        station = YjStationInfo.query.filter_by(id_num=id_num).first()

        if not station:
            return make_response(
                status='error',
                status_code=400,
                msg='服务器没有站点信息'
            )
        # 匹配

        alarm_variable_id = [int(alarm[0]) for alarm in db.session.query(VarAlarmInfo.variable_id).all()]

        # 保存数据
        # value_list = list()
        for v in data['value']:
            # value_model = {
            #     'variable_id': v['variable_id'],
            #     'value': v['value'],
            #     'time': v['time']
            # }
            # value_list.append(value_model)
            value_model = Value(
                variable_id=v['variable_id'],
                value=v['value'],
                time=v['time']
            )
            db.session.add(value_model)
            # value_list.append(value_model)

        # db.session.bulk_save_objects(value_list)

        response = make_response(
            status='OK',
            status_code=200,
            id_num=id_num,
        )

        db.session.commit()

        return response
