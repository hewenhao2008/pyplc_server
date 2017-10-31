# coding=utf-8

from api_templete import ApiResource
from web_server.ext import db
from web_server.models import StationAlarm
from web_server.rest.parsers import station_alarm_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class StationAlarmResource(ApiResource):
    def __init__(self):
        self.args = station_alarm_parser.parse_args()
        super(StationAlarmResource, self).__init__()

    def search(self):
        alarm_id = self.args['id']
        id_num = self.args['id_num']
        code = self.args['code']

        min_time = self.args['min_time']
        max_time = self.args['max_time']

        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = StationAlarm.query

        if alarm_id is not None:
            query = query.filter_by(id=alarm_id)

        if id_num is not None:
            query = query.filter_by(id_num=id_num)

        if code is not None:
            query = query.filter_by(code=code)

        if min_time is not None:
            query = query.filter(StationAlarm.time > min_time)

        if max_time is not None:
            query = query.filter(StationAlarm.time < max_time)

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
            data['code'] = m.code
            data['note'] = m.note
            data['time'] = m.time

            info.append(data)

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = station_alarm_parser.parse_args()

        # 添加
        model = StationAlarm(
            id_num=args['id_num'],
            code=args['code'],
            note=args['note'],
            time=args['time']
        )

        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = station_alarm_parser.parse_args()

        model_id = args['id']

        # 修改
        model = StationAlarm.query.get(model_id)

        if not model:
            return err_not_found()

        if args['id_num'] is not None:
            model.id_num = args['id_num']

        if args['code'] is not None:
            model.code = args['code']

        if args['note'] is not None:
            model.note = args['note']

        if args['time'] is not None:
            model.time = args['time']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
