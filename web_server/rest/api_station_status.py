# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, TransferLog
from web_server.rest.parsers import status_parser, status_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class StatusResource(ApiResource):
    def __init__(self):
        self.args = status_parser.parse_args()
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10
        super(StatusResource, self).__init__()

    def search(self, model_id=None):

        if not model_id:
            model_id = self.args['id']

        station_id = self.args['station_id']
        note = self.args['note']

        min_time = self.args['min_time']
        max_time = self.args['max_time']
        order_time = self.args['order_time']
        limit = self.args['limit']

        query = TransferLog.query

        if model_id is not None:
            query = query.filter_by(id=model_id)

        if station_id is not None:
            query = query.filter(TransferLog.station_id.in_(station_id))

        if note is not None:
            query = query.filter(note=note)

        if min_time is not None:
            query = query.filter(TransferLog.time > min_time)

        if max_time is not None:
            query = query.filter(TransferLog.time < max_time)

        if order_time is not None:
            query = query.order_by(TransferLog.time.desc())

        # if limit:
        #     query = query.limit(limit)

        if self.page is not None:
            pagination = query.paginate(self.page, self.per_page, False)
            self.total = pagination.total
            self.per_page = pagination.per_page
            self.pages = pagination.pages
            query = pagination.items
        elif limit:
            # time1 = time.time()
            # station_id_list = set((a.station_id for a in query))
            station_id_list = station_id
            query = [model
                     for s_id in station_id_list
                     for model in query.filter(TransferLog.station_id == s_id).limit(limit).all()
                     ]
            # time2 = time.time()
            # print time2 - time1
        else:
            query = query.all()

        # print query.all()

        return query

    def information(self, models):

        info = [
            dict(id=m.id,
                 station_id=m.station_id,
                 level=m.level,
                 note=m.note,
                 time=m.time)
            for m in models
        ]

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total, self.per_page)

        return rp

    def put(self):
        args = status_put_parser.parse_args()

        model = TransferLog(
            station_id=args['station_id'],
            level=args['level'],
            time=args['time'],
            note=args['note'],
        )
        db.session.add(model)
        db.session.commit()
        return rp_create()

    def patch(self):
        args = status_put_parser.parse_args()

        model_id = args['id']

        model = TransferLog.query.get(model_id)

        if not model:
            return err_not_found()

        if args['station_id']:
            model.station_name = args['station_id']

        if args['level']:
            model.level = args['level']

        if args['time']:
            model.time = args['time']

        if args['note']:
            model.note = args['note']

        db.session.add(model)
        db.session.commit()
        return rp_modify()
