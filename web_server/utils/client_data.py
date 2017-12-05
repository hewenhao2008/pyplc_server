# coding=u8
import time
from web_server.models import serialize, VarAlarmInfo, db


def config_data(station_model):
    # 获取属于该终端的四个表的数据
    time1 = time.time()
    station_data = serialize(station_model)

    plcs = station_model.plcs
    plc_data = [
        serialize(plc)
        for plc in plcs
    ]

    groups = [
        model
        for plc in plcs
        for model in plc.groups
    ]

    group_data = [
        serialize(group)
        for group in groups]

    variables = [
        model.variable
        for group in groups
        for model in group.variables
    ]

    variable_data = [
        serialize(variable)
        for variable in variables
    ]

    group_var_data = [
        serialize(model)
        for group in groups
        for model in group.variables
    ]

    alarm_info = []
    for v in variables:
        if v.alarms:
            alarm_info += v.alarms

    alarm_data = [
        serialize(model)
        for model in alarm_info
    ]

    time2 = time.time()
    print(time2 - time1)

    data = {
        'stations': station_data,
        'plcs': plc_data,
        'groups': group_data,
        'variables': variable_data,
        'variables_groups': group_var_data,
        'alarm': alarm_data,
    }

    return data


def config_data2(station_model):
    # time1 = time.time()
    station_data = serialize(station_model)
    plc_data = []
    group_data = []
    group_var_data = []
    variable_data = []
    alarm_data = []
    plcs = station_model.plcs.all()
    for plc in plcs:

        plc_data.append(serialize(plc))

        groups = plc.groups.all()
        for group in groups:

            group_data.append(serialize(group))

            group_variables = group.variables
            # print(group_variables)

            for g_v in group_variables:
                group_var_data.append(serialize(g_v))

                variable = g_v.variable
                # print(variable)

                variable_data.append(serialize(variable))

                alarms = variable.alarms.all()

                # print(alarms)
                for alarm in alarms:
                    alarm_data.append(serialize(alarm))

    # time2 = time.time()
    # print(time2 - time1)

    data = {
        'stations': station_data,
        'plcs': plc_data,
        'groups': group_data,
        'variables': variable_data,
        'variables_groups': group_var_data,
        'alarm': alarm_data,
    }

    return data
