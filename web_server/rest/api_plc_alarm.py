# coding=utf-8

from api_templete import ApiResource
from web_server.ext import db
from web_server.models import PLCAlarm
from web_server.rest.parsers import plc_alarm_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class PLCAlarmResource(ApiResource):
    def __init__(self):
        self.args = plc_alarm_parser.parse_args()
        super(PLCAlarmResource, self).__init__()

    def search(self):
        alarm_id = self.args['id']
        plc_id = self.args['plc_id']
        level = self.args['level']
        id_num = self.args['id_num']

        min_time = self.args['min_time']
        max_time = self.args['max_time']

        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = PLCAlarm.query

        if alarm_id is not None:
            query = query.filter_by(id=alarm_id)

        if id_num is not None:
            query = query.filter_by(id_num=id_num)

        if plc_id is not None:
            query = query.filter_by(plc_id=plc_id)

        if level is not None:
            query = query.filter_by(level=level)

        if min_time is not None:
            query = query.filter(PLCAlarm.time > min_time)

        if max_time is not None:
            query = query.filter(PLCAlarm.time < max_time)

        if page is not None:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        return query

    def information(self, models):

        # 将查询到对象数据填入字典
        info = []
        for m in models:
            data = dict()
            data['id'] = m.id
            data['id_num'] = m.id_num
            data['plc_id'] = m.plc_id
            data['level'] = m.level
            data['note'] = m.note
            data['time'] = m.time

            info.append(data)

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = plc_alarm_parser.parse_args()

        # 添加
        model = PLCAlarm(
            id_num=args['id_num'],
            plc_id=args['plc_id'],
            level=args['level'],
            note=args['note'],
            time=args['time']
        )

        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = plc_alarm_parser.parse_args()

        model_id = args['id']

        # 修改
        model = PLCAlarm.query.get(model_id)

        if model is None:
            return err_not_found()

        if args['id_num'] is not None:
            model.id_num = args['id_num']

        if args['plc_id'] is not None:
            model.plc_id = args['plc_id']

        if args['level'] is not None:
            model.level = args['level']

        if args['note'] is not None:
            model.note = args['note']

        if args['time'] is not None:
            model.time = args['time']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
