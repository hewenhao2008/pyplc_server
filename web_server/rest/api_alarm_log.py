# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, VarAlarmLog, VarAlarmInfo, YjVariableInfo, YjGroupInfo
from web_server.rest.parsers import alarm_parser, alarm_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class AlarmLogResource(ApiResource):
    def __init__(self):

        self.args = alarm_parser.parse_args()
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10
        super(AlarmLogResource, self).__init__()

    def search(self):

        model_id = self.args['id']

        status = self.args['status']
        alarm_id = self.args['alarm_id']
        plc_id = self.args['plc_id']
        variable_id = self.args['variable_id']
        alarm_type = self.args['alarm_type']
        all_alarm_id = self.args['all_alarm_id']

        min_time = self.args['min_time']
        max_time = self.args['max_time']
        order_time = self.args['order_time']
        limit = self.args['limit']

        query = VarAlarmLog.query

        if model_id is not None:
            query = query.filter_by(id=model_id)

        if alarm_type is not None:
            query = query.join(VarAlarmInfo, VarAlarmInfo.alarm_type.in_(alarm_type))

        if plc_id is not None:
            query = query.join(VarAlarmInfo, YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.plc_id.in_(plc_id))

        if variable_id is not None:
            query = query.join(VarAlarmInfo, YjVariableInfo).filter(YjVariableInfo.id.in_(variable_id))

        if alarm_id is not None:
            query = query.filter(VarAlarmLog.alarm_id.in_(alarm_id))

        if status is not None:
            query = query.filter_by(status=status)

        if min_time is not None:
            query = query.filter(VarAlarmLog.time > min_time)

        if max_time is not None:
            query = query.filter(VarAlarmLog.time < max_time)

        if order_time is not None:
            query = query.order_by(VarAlarmLog.time.desc())

        if all_alarm_id is not None:
            sql = 'select var_alarm_info.id from var_alarm_info'
            models = db.engine.execute(sql).fetchall()
            alarm_id = [model[0] for model in models]

        # if limit:
        #     query = query.limit(limit)

        if self.page is not None:
            pagination = query.paginate(self.page, self.per_page, False)
            self.total = pagination.total
            self.per_page = pagination.per_page
            self.pages = pagination.pages
            query = pagination.items

        elif limit is not None:
            query = [
                model
                for a in alarm_id
                for model in
                VarAlarmLog.query.filter(VarAlarmLog.alarm_id == a).limit(limit).all()
            ]
        else:
            query = query.all()

        # print query.all()

        return query

    def information(self, models):

        info = list()

        for m in models:
            data = dict()
            data['id'] = m.id
            data['alarm_id'] = m.alarm_id
            data['time'] = m.time
            data['status'] = m.status

            alarm_info = m.var_alarm_info
            data['note'] = m.var_alarm_info.note if alarm_info else None
            data['alarm_type'] = m.var_alarm_info.alarm_type if alarm_info else None
            data['variable_id'] = m.var_alarm_info.variable_id if alarm_info else None

            var = m.var_alarm_info.yjvariableinfo if alarm_info else None

            data['variable_name'] = m.var_alarm_info.yjvariableinfo.variable_name if var else None

            group = m.var_alarm_info.yjvariableinfo.yjgroupinfo if var else None
            data['plc_id'] = group.plc_id if group else None

            plc = m.var_alarm_info.yjvariableinfo.yjgroupinfo.yjplcinfo if group else None
            data['plc_name'] = plc.plc_name if plc else None
            data['station_id'] = plc.station_id if plc else None

            station = plc.yjstationinfo if plc else None
            data['station_name'] = station.station_name if station else None

            info.append(data)

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total, self.per_page)

        return rp

    def put(self):
        args = alarm_put_parser.parse_args()

        model = VarAlarmLog(
            alarm_id=args['alarm_id'],
            status=args['status'],
            time=args['time'],
        )
        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = alarm_put_parser.parse_args()

        model_id = args['id']

        model = VarAlarmLog.query.get(model_id)

        if not model:
            return err_not_found()

        if args['alarm_id']:
            model.alarm_id = args['alarm_id']

        if args['status']:
            model.status = args['status']

        if args['time']:
            model.time = args['time']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
