# coding=utf-8
from flask import jsonify, current_app

from api_templete import ApiResource
from web_server.ext import db
from web_server.models import YjPLCInfo, YjGroupInfo, YjVariableInfo
from web_server.rest.parsers import variable_parser, variable_put_parser
from web_server.utils.err import err_not_found, variable_overfulfil
from web_server.utils.response import rp_create, rp_modify, rp_get


class VariableResource(ApiResource):
    def __init__(self):
        self.args = variable_parser.parse_args()
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10
        super(VariableResource, self).__init__()

    def search(self):
        variable_id = self.args['id']

        variable_name = self.args['variable_name']
        plc_id = self.args['plc_id']
        plc_name = self.args['plc_name']
        group_id = self.args['group_id']
        group_name = self.args['group_name']

        query = YjVariableInfo.query

        if variable_id is not None:
            query = query.filter_by(id=variable_id)

        if variable_name is not None:
            query = query.filter_by(variable_name=variable_name)

        if group_id is not None:
            query = query.filter(YjVariableInfo.group_id.in_(group_id))

        if group_name is not None:
            query = query.join(YjGroupInfo, YjGroupInfo.group_name == group_name)

        if plc_id is not None:
            query = query.join(YjGroupInfo).filter(YjGroupInfo.plc_id.in_(plc_id))

        if plc_name is not None:
            query = query.join(YjGroupInfo, YjPLCInfo).filter(YjPLCInfo.plc_name == plc_name)

        if self.page is not None:
            pagination = query.paginate(self.page, self.per_page, False)
            self.total = pagination.total
            self.per_page = pagination.per_page
            self.pages = pagination.pages
            query = pagination.items
        else:
            query = query.all()

        return query

    def information(self, models):

        info = []
        for m in models:

            data = dict()
            data['id'] = m.id
            data['variable_name'] = m.variable_name
            data['group_id'] = m.group_id
            data['area'] = m.area
            data['db_num'] = m.db_num
            data['address'] = m.address
            data['data_type'] = m.data_type
            data['rw_type'] = m.rw_type
            data['upload'] = m.upload
            data['acquisition_cycle'] = m.acquisition_cycle
            data['server_record_cycle'] = m.server_record_cycle
            data['note'] = m.note
            data['ten_id'] = m.ten_id
            data['item_id'] = m.item_id
            data['write_value'] = m.write_value

            group = m.yjgroupinfo
            if group:
                data['group_name'] = group.group_name
                data['plc_id'] = group.plc_id
                plc = group.yjplcinfo
            else:
                data['group_name'] = None
                data['plc_id'] = None
                plc = None

            if plc:
                data['plc_name'] = plc.plc_name
            else:
                data['plc_name'] = None

            info.append(data)

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total, self.per_page)

        return rp

    def put(self):
        args = variable_put_parser.parse_args()

        # 检查站点已存在变量数量，防止超过规定上限
        if args['group_id'] is not None:
            plc_id = YjGroupInfo.query.filter_by(id=args['group_id']).first().yjplcinfo.id
            station_variable_count = YjVariableInfo.query.join(YjGroupInfo).filter(
                YjGroupInfo.plc_id == plc_id).count()
            if station_variable_count >= current_app.config['VARIABLE_COUNT']:
                return variable_overfulfil()

        variable = YjVariableInfo(
            variable_name=args['variable_name'],
            group_id=args['group_id'],
            db_num=args['db_num'],
            address=args['address'],
            area=args['area'],
            data_type=args['data_type'],
            rw_type=args['rw_type'],
            upload=args['upload'],
            acquisition_cycle=args['acquisition_cycle'],
            server_record_cycle=args['server_record_cycle'],
            note=args['note'],
            ten_id=args['ten_id'],
            item_id=args['item_id'],
            write_value=args['write_value']
        )

        db.session.add(variable)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = variable_put_parser.parse_args()

        variable_id = args['id']

        variable = YjVariableInfo.query.get(variable_id)

        if not variable:
            return err_not_found()

        if args['variable_name'] is not None:
            variable.variable_name = args['variable_name']

        if args['group_id'] is not None:
            variable.group_id = args['group_id']

        if args['db_num'] is not None:
            variable.db_num = args['db_num']

        if args['address'] is not None:
            variable.address = args['address']

        if args['data_type'] is not None:
            variable.data_type = args['data_type']

        if args['rw_type'] is not None:
            variable.rw_type = args['rw_type']

        if args['upload'] is not None:
            variable.upload = args['upload']

        if args['acquisition_cycle'] is not None:
            variable.acquisition_cycle = args['acquisition_cycle']

        if args['server_record_cycle'] is not None:
            variable.server_record_cycle = args['server_record_cycle']

        if args['note'] is not None:
            variable.note = args['note']

        if args['ten_id'] is not None:
            variable.ten_id = args['ten_id']

        if args['item_id'] is not None:
            variable.item_id = args['item_id']

        if args['write_value'] is not None:
            variable.write_value = args['write_value']

        if args['area'] is not None:
            variable.area = args['area']

        db.session.add(variable)
        db.session.commit()

        return rp_modify()
