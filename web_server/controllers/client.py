# coding=utf-8

from os import path
import time
from flask import Blueprint, request, jsonify
import json
import zlib

# from mc import mc
from web_server.ext import db
from web_server.models import (serialize, YjStationInfo,
                               Value, VarAlarm, VarAlarmInfo, VarAlarmLog, StationAlarm, PLCAlarm)
from web_server.util import get_data_from_query, get_data_from_model, encryption, decryption
from web_server.utils.aliyun_sms import sms_alarm
from web_server.utils.response import make_response

client_blueprint = Blueprint(
    'client',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'client'),
    url_prefix='/client'
)


@client_blueprint.route('/beats', methods=['POST'])
def beats():
    # 获取心跳数据
    data = request.get_json(force=True)
    # data = decryption(rv)

    # 根据id_num查询终端数据模型
    station = YjStationInfo.query.filter_by(id_num=data["id_num"]).first()
    print(1)
    if station:
        # 记录连接时间
        station.con_time = int(time.time())

        # if int(station.version) != int(data["version"]):
        #     station.modification = 1
        # else:
        #     station.modification = 0

        db.session.add(station)

        # 记录变量报警信息
        if 'alarm_log' in data.keys() and data['alarm_log']:
            for log in data['alarm_log']:
                l = VarAlarmLog(
                    alarm_id=log['alarm_id'],
                    time=log['time'],
                    confirm=log['confirm']
                )
                db.session.add(l)
            print(2)
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
        print(3)
        # 记录PLC故障信息
        if data['plc_alarms']:
            for plc_alarm in data['plc_alarms']:
                alarm = PLCAlarm(
                    id_num=plc_alarm['id_num'],
                    plc_id=plc_alarm['plc_id'],
                    level=plc_alarm['level'],
                    note=plc_alarm['note'],
                    time=plc_alarm['time']
                )
                db.session.add(alarm)
        print(4)
        modification = station.modification
        status = 'ok'

        # data = encryption(data)

    else:
        modification = 0
        status = 'error'
    print(5)
    # 返回信息
    data = {
        "modification": modification,
        "status": status
    }
    db.session.commit()

    return jsonify(data)


@client_blueprint.route('/config', methods=['POST'])
def set_config():
    if request.method == 'POST':
        data = request.get_json(force=True)

        station = db.session.query(YjStationInfo).filter_by(id_num=data["id_num"]).first()

        if not station:
            response = make_response(
                'error',
                400,
                msg='站点信息不存在'
            )
            return response
        # data = decryption(data)

        # 获取属于该终端的四个表的数据
        data = {
            "YjStationInfo": serialize(station),
            "YjPLCInfo": [serialize(plc)
                          for plc in station.plcs],
            "YjGroupInfo": [serialize(group)
                            for plc in station.plcs
                            for group in plc.groups],
            "YjVariableInfo": [serialize(variable)
                               for plc in station.plcs
                               for group in plc.groups
                               for variable in group.variables]
        }

        # 将本次发送过配置的站点数据表设置为无更新
        station.modification = 0

        db.session.add(station)
        db.session.commit()

        # data = encryption(data)
        # data = json.dumps(data)
        # data = zlib.compress(data)

        response = make_response('OK', 200, data=data)
        return response


@client_blueprint.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        # 设置每次上传时最大发送的短信条数
        message_count = 1

        data = request.get_json(force=True)
        # data = decryption(data)
        # data = zlib.decompress(data)
        # data = json.loads(data)

        # 验证上传数据
        id_num = data["id_num"]
        version = data["version"]

        print(data, version, int(version))
        # 查询服务器是否有正在上传的站信息
        station = YjStationInfo.query.filter_by(id_num=id_num).first()
        print(type(station.version))

        if not station:
            return make_response(
                status='error',
                status_code=400,
                msg='服务器没有站点信息'
            )
        # 查询上传信息的版本是否匹配
        try:
            pass
            # assert isinstance(int(station.version), int)
            # assert (int(station.version) == int(version))
        # 不匹配
        except (AssertionError, TypeError) as e:
            response = make_response('version error:' + str(e), 403)

        # 匹配
        else:

            # 获取报警变量id
            # try:
            #     alarm_variable_id = mc.get('alarm_variable_id')
            #     print(alarm_variable_id)
            # except Exception, e:
            #     print('获取缓存失败' + str(e))
            # else:
            alarm_variable_id = [int(alarm[0]) for alarm in db.session.query(VarAlarmInfo.variable_id).all()]

            # 保存数据

            for v in data["value"]:
                value = Value(
                    variable_id=v["variable_id"],
                    value=v["value"],
                    time=v["time"]
                )
                db.session.add(value)

                print(alarm_variable_id)
                if int(v['variable_id']) in alarm_variable_id:
                    print('报警')
                    try:
                        # 获取历史报警
                        last_log = VarAlarmLog.query.join(VarAlarmInfo, VarAlarmInfo.variable_id == v['variable_id']). \
                            filter(VarAlarmLog.alarm_id == VarAlarmInfo.id).order_by(VarAlarmLog.time.desc()).first()
                        status = int(v['value'])

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

                    except ValueError as e:
                        print(e)

            response = make_response(
                status='OK',
                status_code=200,
                id_num=id_num,
                version=version
            )

        db.session.commit()

        return response
