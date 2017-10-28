# coding=utf-8

from api_templete import ApiResource
from web_server.ext import db
from web_server.models import YjStationInfo, YjPLCInfo
from web_server.rest.parsers import plc_parser, plc_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class PLCResource(ApiResource):
    def __init__(self):
        self.args = plc_parser.parse_args()
        super(PLCResource, self).__init__()
        self.query = YjPLCInfo.query

    def search(self):

        plc_id = self.args['id']
        plc_name = self.args['plc_name']
        station_id = self.args['station_id']
        station_name = self.args['station_name']

        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = YjPLCInfo.query

        if plc_id:
            query = query.filter_by(id=plc_id)

        if plc_name:
            query = query.filter_by(plc_name=plc_name)

        if station_id:
            query = query.filter(YjPLCInfo.station_id.in_(station_id))

        if station_name:
            query = query.join(YjStationInfo, YjStationInfo.station_name == station_name)

        if limit:
            query = query.limit(limit)

        # print(query)

        if page:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        self.query = query

        return query

    def information(self, models):

        info = []
        for m in models:
            station = m.yjstationinfo

            data = dict()
            data['id'] = m.id
            data['plc_name'] = m.plc_name
            data['station_id'] = m.station_id
            data['note'] = m.note
            data['ip'] = m.ip
            data['mpi'] = m.mpi
            data['type'] = m.type
            data['plc_type'] = m.plc_type
            data['ten_id'] = m.ten_id
            data['item_id'] = m.item_id
            data['rack'] = m.rack
            data['slot'] = m.slot
            data['tcp_port'] = m.tcp_port

            if station:
                data['station_id_num'] = station.id_num
                data['station_name'] = station.station_name
            else:
                data['station_id_num'] = None
                data['station_name'] = None

            info.append(data)

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = plc_put_parser.parse_args()

        self.query = []
        plc = YjPLCInfo(
            plc_name=args['plc_name'],
            station_id=args['station_id'],
            note=args['note'],
            ip=args['ip'],
            mpi=args['mpi'],
            type=args['type'],
            plc_type=args['plc_type'],
            ten_id=args['ten_id'],
            item_id=args['item_id'],
            rack=args['rack'],
            slot=args['slot'],
            tcp_port=args['tcp_port']
        )

        db.session.add(plc)
        db.session.commit()
        self.new_id = plc.id
        return rp_create()

    def patch(self):

        args = plc_put_parser.parse_args()

        plc_id = args['id']

        plc = YjPLCInfo.query.get(plc_id)
        self.query = [].append(plc)
        print self.query
        if not plc:
            return err_not_found()

        if args['plc_name'] is not None:
            plc.plc_name = args['plc_name']

        if args['station_id'] is not None:
            plc.station_id = args['station_id']

        if args['note'] is not None:
            plc.note = args['note']

        if args['ip'] is not None:
            plc.ip = args['ip']

        if args['mpi'] is not None:
            plc.mpi = args['mpi']

        if args['type'] is not None:
            plc.type = args['type']

        if args['plc_type'] is not None:
            plc.plc_type = args['plc_type']

        if args['ten_id'] is not None:
            plc.ten_id = args['ten_id']

        if args['item_id'] is not None:
            plc.item_id = args['item_id']

        if args['rack'] is not None:
            plc.rack = args['rack']

        if args['slot'] is not None:
            plc.slot = args['slot']

        if args['tcp_port'] is not None:
            plc.tcp_port = args['tcp_port']

        db.session.add(plc)
        db.session.commit()

        return rp_modify()
