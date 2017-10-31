# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, VarAlarmInfo, YjVariableInfo, YjGroupInfo
from web_server.rest.parsers import alarm_info_parser, alarm_info_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class AlarmInfoResource(ApiResource):
    def __init__(self):
        self.args = alarm_info_parser.parse_args()
        super(AlarmInfoResource, self).__init__()

    def search(self):

        model_id = self.args['id']

        plc_id = self.args['plc_id']
        variable_id = self.args['variable_id']
        alarm_type = self.args['alarm_type']
        note = self.args['note']

        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = VarAlarmInfo.query

        if model_id is not None:
            query = query.filter_by(id=model_id)

        if alarm_type is not None:
            query = query.filter(VarAlarmInfo.alarm_type == alarm_type)

        if plc_id is not None:
            query = query.join(YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.plc_id.in_(plc_id))

        if variable_id is not None:
            query = query.filter(VarAlarmInfo.variable_id.in_(variable_id))

        if note is not None:
            query = query.filter(VarAlarmInfo.note == note)

        if limit is not None:
            query = query.limit(limit)

        if page is not None:
            query = query.paginate(page, per_page, False).items

        else:
            query = query.all()

        # print query.all()

        return query

    def information(self, models):

        info = [
            dict(
                id=m.id,
                plc_id=m.yjvariableinfo.yjgroupinfo.plc_id
                if m.yjvariableinfo and m.yjvariableinfo.yjgroupinfo else None,
                variable_id=m.variable_id,
                variable_name=m.yjvariableinfo.variable_name if m.yjvariableinfo else None,
                alarm_type=m.alarm_type,
                note=m.note,
                is_send_message=m.is_send_message
            )
            for m in models
        ]

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = alarm_info_put_parser.parse_args()

        model = VarAlarmInfo(
            variable_id=args['variable_id'],
            alarm_type=args['alarm_type'],
            note=args['note'],
            is_send_message=args['is_send_message']
        )
        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = alarm_info_put_parser.parse_args()

        model_id = args['id']

        model = VarAlarmInfo.query.get(model_id)

        if not model:
            return err_not_found()

        if args['variable_id'] is not None:
            model.variable_id = args['variable_id']

        if args['alarm_type'] is not None:
            model.alarm_type = args['alarm_type']

        if args['note'] is not None:
            model.note = args['note']

        if args['is_send_message'] is not None:
            model.is_send_message = args['is_send_message']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
