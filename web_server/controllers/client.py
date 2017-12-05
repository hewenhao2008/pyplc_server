# coding=utf-8

from os import path
import logging
import time
from flask import Blueprint, request, jsonify
import platform

from mc import mc
from web_server.ext import db
from web_server.models import (YjStationInfo, Value, VarAlarmInfo, VarAlarmLog, StationAlarm, PLCAlarm, VarAlarm,
                               TerminalInfo, engine)
from web_server.util import encryption_server, decryption_server
from web_server.utils.aliyun_sms import sms_alarm
from web_server.utils.response import make_response
from web_server.utils.client_data import config_data, config_data2

client_blueprint = Blueprint(
    'client',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'client'),
    url_prefix='/client'
)


def station_exist(id_num):
    station_id_num = mc.get('id_num')
    exist = False
    if station_id_num:
        if id_num in station_id_num:
            exist = True
            return exist

    station_model = YjStationInfo.query.filter_by(id_num=id_num).first()
    if station_model:
        exist = True
        if station_id_num:
            station_id_num.append(station_model.id_num)
        else:
            station_id_num = [station_model.id_num]

        mc.set('id_num', station_id_num)

    return exist


def get_alarm(v, station, message_count, time):
    # 获取历史报警
    # print(v)
    last_log = VarAlarmLog.query.join(VarAlarmInfo, VarAlarmInfo.variable_id == v['id']).filter(
        VarAlarmLog.alarm_id == VarAlarmInfo.id).order_by(VarAlarmLog.time.desc()).first()
    status = v['is_alarm']

    # 历史报警不存在，写入历史报警和当前报警
    # print('status', status, last_log)
    if last_log is None:
        alarm_info = VarAlarmInfo.query.filter_by(variable_id=v['id']).first()
        if status == 1:
            log = VarAlarmLog(
                alarm_id=alarm_info.id,
                time=time,
                status=status
            )
            db.session.add(log)

            alarm = VarAlarm(
                alarm_id=alarm_info.id,
                time=time
            )
            db.session.add(alarm)

            # 发送短信
            # if alarm_info.is_send_message and station.phone and station.station_name:
            #     print('发送短信')
            #     if message_count > 0:
            #         sms_alarm(station.phone, {'name': str(station.station_name)})
            #         message_count -= 1
    else:
        # 历史报警存在，检查状态。相同不做处理，不相同时，记录本次状态。同时增加或删除当前报警表内该变量信息。
        # print(last_log.status != status)
        if last_log.status != status:
            log = VarAlarmLog(
                alarm_id=last_log.alarm_id,
                time=time,
                status=status
            )
            db.session.add(log)
            print(status, type(status))
            if status == 1:
                alarm = VarAlarm(
                    alarm_id=last_log.alarm_id,
                    time=time
                )
                db.session.add(alarm)
                # 发送短信
                # alarm_info = VarAlarmInfo.query.filter_by(id=last_log.alarm_id).first()
                # print(alarm_info)
                # print(alarm_info.is_send_message, station.phone, station.station_name)
                # if alarm_info.is_send_message and station.phone and station.station_name:
                #     print('发短信2')
                #     if message_count > 0:
                #         sms_alarm(station.phone, {'name': str(station.station_name)})
                #         message_count -= 1
            elif status == 0:
                alarm = VarAlarm.query.filter(VarAlarm.alarm_id == last_log.alarm_id).first()
                if alarm:
                    db.session.delete(alarm)



@client_blueprint.route('/beats', methods=['POST'])
def beats():
    # 设置每次上传时最大发送的短信条数
    message_count = 1

    # 获取心跳数据
    rv = request.get_data()

    data = decryption_server(rv)

    # 根据id_num查询终端数据模型
    station = YjStationInfo.query.filter_by(id_num=data['id_num']).first()

    if station:
        # 记录连接时间
        station.con_time = int(time.time())

        db.session.add(station)

        # print(data['data_alarms'])
        # 记录变量报警信息
        if data['data_alarms']:
            for alarm in data['data_alarms']:
                for log in alarm['data']:
                    get_alarm(log, station, message_count, alarm['time'])

        logging.debug('记录变量报警完成')

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
        logging.debug('记录终端故障完成')

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
        logging.debug('记录PLC故障完成')

        # 记录终端设备状态
        if data['station_info']:
            station_info = data['station_info']
            info = TerminalInfo.query.filter_by(station_id=station.id).first()
            if not info:
                info = TerminalInfo()
                info.station_id = station.id
            info.cpu_percent = station_info['cpu_percent']
            info.boot_time = station_info['boot_time']
            info.total_usage = station_info['total_usage']
            info.free_usage = station_info['free_usage']
            info.usage_percent = station_info['usage_percent']
            info.total_memory = station_info['total_memory']
            info.free_memory = station_info['free_memory']
            info.memory_percent = station_info['memory_percent']
            info.bytes_sent = station_info['bytes_sent']
            info.bytes_recv = station_info['bytes_recv']
            info.cpu_percent = station_info['cpu_percent']

            db.session.merge(info)

        is_modify = station.is_modify
        status = 'ok'

    else:
        is_modify = 0
        status = 'error'

    logging.debug('心跳记录完成，返回确认信息')

    # 返回信息
    data = {
        'is_modify': is_modify,
        'status': status
    }
    # data = encryption_server(data)
    db.session.commit()

    return jsonify(data)


@client_blueprint.route('/config', methods=['POST'])
def set_config():
    if request.method == 'POST':
        data = request.get_json(force=True)

        id_num = data['id_num']

        exist = station_exist(id_num)

        if not exist:
            response = make_response(
                'error',
                400,
                msg='站点信息不存在'
            )
            return response

        data = config_data2(id_num)

        # 压缩
        data = encryption_server(data)

        response = make_response('OK', 200, data=data, platform=platform.uname())
        return response


@client_blueprint.route('/confirm/config', methods=['POST'])
def confirm_config():
    if request.method == 'POST':
        data = request.get_json()

        station = db.session.query(YjStationInfo).filter_by(id_num=data['id_num']).first()

        # 将本次发送过配置的站点数据表设置为无更新
        station.is_modify = 0

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
        station_id_num = mc.get('id_num')
        station = False
        if station_id_num:
            if id_num in station_id_num:
                station = True
        else:
            station = YjStationInfo.query.filter_by(id_num=id_num).first()

        if not station:
            print('服务器没有站点信息')
            return make_response(
                status='error',
                status_code=400,
                msg='服务器没有站点信息'
            )
        # 匹配
        # 保存数据
        time1 = time.time()
        value_list = list()
        print(len(data['value']))
        for v in data['value']:
            value_model = {
                'variable_id': v['i'],
                'value': v['v'],
                'time': v['t']
            }
            value_list.append(value_model)
        db.session.bulk_insert_mappings(Value, value_list)
        db.session.commit()
        time2 = time.time()
        print(time2 - time1)
        response = make_response(
            status='OK',
            status_code=200,
            id_num=id_num,
        )

        return response
