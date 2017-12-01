# coding=utf-8

import hmac
import base64
import zlib
import json

from flask import jsonify


def encryption_server(dict_data):
    """
    
    :param dict_data: dict
    :return: base64encode str
    """

    str_data = json.dumps(dict_data)
    zlib_data = zlib.compress(str_data)

    base64_data = base64.b64encode(zlib_data)

    return base64_data


def decryption_server(zlib_data):
    """
    
    :param zlib_data: request.get_data()
    :return: dict
    """

    str_data = zlib.decompress(zlib_data)
    dict_data = json.loads(str_data)

    return dict_data


def get_data_from_query(models):
    # 输入session.query()查询到的模型实例列表,读取每个实例每个值,放入列表返回
    data_list = []
    for model in models:
        model_column = {}
        for c in model.__table__.columns:
            model_column[c.name] = getattr(model, c.name, None)
        data_list.append(model_column)
    return data_list


def get_data_from_model(model):
    # 读取一个模型实例中的每一项与值，放入字典
    model_column = {}
    for c in model.__table__.columns:
        model_column[c.name] = getattr(model, c.name, None)
    return model_column


def configuration(station_model):
    """
    读取staion表数据,根据外链,读出该station下的plc、group variable的数据.每一项数据为一个字典,每个表中所有数据存为一个列表.

    :param station_model: 
    :return: 
    """
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
    data = {
        "YjStationInfo": station_config,
        "YjPLCInfo": plcs_config,
        "YjGroupInfo": groups_config,
        "YjVariableInfo": variables_config
    }

    return data
