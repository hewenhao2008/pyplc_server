# coding=utf-8

from os import path
import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app, flash, Config

from flask_login import login_user, logout_user, user_logged_in, login_required, current_user
from flask_principal import identity_loaded, identity_changed, UserNeed, RoleNeed, Identity, AnonymousIdentity

from web_server.ext import db, csrf, api
from web_server.models import (serialize, YjStationInfo, YjPLCInfo, YjGroupInfo, YjVariableInfo,
                               Value, VarAlarm, VarAlarmInfo, VarAlarmLog, StationAlarm, PLCAlarm)
from web_server.util import get_data_from_query, get_data_from_model
from web_server.utils.aliyun_sms import sms_alarm
# from web_server import mc

client_blueprint = Blueprint(
    'client',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'client'),
    url_prefix='/client'
)


def make_response(status, status_code, **kwargs):
    msg = {
        'status': status
    }
    msg.update(kwargs)
    response = jsonify(msg)
    response.status_code = status_code

    return response


def configuration(station_model):
    # 读取staion表数据,根据外链,读出该station下的plc、group variable的数据.每一项数据为一个字典,每个表中所有数据存为一个列表.
    plcs_config = []
    groups_config = []
    variables_config = []

    station_config = get_data_from_model(station_model)

    plcs = station_model.plcs.all()
    if plcs:
        plcs_config = get_data_from_query(plcs)
        for plc in plcs:

            groups = plc.groups.all()
            if groups:
                groups_config += get_data_from_query(groups)

            variables = plc.variables.all()
            if variables:
                variables_config += get_data_from_query(variables)

    # 包装数据
    data = {"YjStationInfo": station_config, "YjPLCInfo": plcs_config,
            "YjGroupInfo": groups_config, "YjVariableInfo": variables_config}

    return data


@client_blueprint.route('/beats', methods=['POST'])
def beats():
    # 获取心跳数据
    data = request.get_json(force=True)
    # data = decryption(rv)

    # 根据id_num查询终端数据模型
    station = YjStationInfo.query.filter_by(id_num=data["id_num"]).first()
    if station:
        # 记录连接时间
        station.con_time = int(time.time())

        # if int(station.version) != int(data["version"]):
        #     station.modification = 1
        # else:
        #     station.modification = 0

        db.session.add(station)

        # 记录变量报警信息
        if 'alarm_log' in data.keys():
            for log in data['alarm_log']:
                l = VarAlarmLog(
                    alarm_id=log['alarm_id'],
                    time=log['time'],
                    confirm=log['confirm']
                )
                db.session.add(l)

        # 记录终端故障信息
        for station_alarm in data['station_alarms']:
            alarm = StationAlarm(
                id_num=station_alarm['id_num'],
                code=station_alarm['code'],
                note=station_alarm['note'],
                time=station_alarm['time']
            )
            db.session.add(alarm)

        # 记录PLC故障信息
        for plc_alarm in data['plc_alarms']:
            alarm = PLCAlarm(
                id_num=plc_alarm['id_num'],
                plc_id=plc_alarm['plc_id'],
                level=plc_alarm['level'],
                note=plc_alarm['note'],
                time=plc_alarm['time']
            )
            db.session.add(alarm)

        modification = station.modification
        status = 'ok'

        # data = encryption(data)

    else:
        modification = 0
        status = 'error'

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
        # data = decryption(data)


        # time1 = time.time()
        # data = configuration(station)
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
        # time2 = time.time()
        # print(time2 - time1)

        # 将本次发送过配置的站点数据表设置为无更新
        station.modification = 0

        db.session.add(station)
        db.session.commit()

        # data = encryption(data)
        response = make_response('OK', 200, data=data)
        return response


@client_blueprint.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        data = request.get_json(force=True)
        # data = decryption(data)

        # 验证上传数据
        id_num = data["id_num"]
        version = data["version"]

        # 查询服务器是否有正在上传的站信息
        station = YjStationInfo.query.filter_by(id_num=id_num).first()

        # 查询上传信息的版本是否匹配
        try:
            assert (int(station.version) == int(version))
        # 不匹配
        except AssertionError:
            response = make_response('version error', 403)

        # 匹配
        else:

            # 保存数据
            for v in data["value"]:
                value = Value(
                    variable_id=v["variable_id"],
                    value=v["value"],
                    time=v["time"]
                )
                db.session.add(value)

                try:
                    # 获取历史报警
                    last_log = VarAlarmLog.query.join(VarAlarmInfo, VarAlarmInfo.variable_id == v['variable_id']). \
                        filter(VarAlarmLog.alarm_id == VarAlarmInfo.id).order_by(VarAlarmLog.time.desc()).first()
                    status = int(v['value'])

                    # 历史报警不存在，写入历史报警和当前报警
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
                                sms_alarm(station.phone, {'name': station.station_name})

                    else:
                        # 历史报警存在，检查状态。相同不做处理，不相同时，记录本次状态。同时增加或删除当前报警表内该变量信息。
                        if last_log.status != status:
                            log = VarAlarmLog(
                                alarm_id=last_log.alarm_id,
                                time=v['time'],
                                status=status
                            )
                            db.session.add(log)
                            if status == 1:
                                alarm = VarAlarm(
                                    alarm_id=last_log.alarm_id,
                                    time=v['time']
                                )
                                db.session.add(alarm)

                                # 发送短信
                                if alarm.var_alarm_info.is_send_message and station.phone and station.station_name:
                                    sms_alarm(station.phone, {'name': station.station_name})

                            elif status == 0:
                                alarm = VarAlarm.query.filter(VarAlarm.alarm_id == last_log.alarm_id).first()
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
