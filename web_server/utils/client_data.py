# coding=u8
from web_server.models import serialize


def config_data(station_model):
    # 获取属于该终端的四个表的数据
    station_data = serialize(station_model)

    plcs = station_model.plcs
    plc_data = [
        serialize(plc)
        for plc in plcs]

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

    data = {
        'stations': station_data,
        'plcs': plc_data,
        'groups': group_data,
        'variables': variable_data,
        'variables_groups': group_var_data,
        'alarm': alarm_data
    }

    return data
