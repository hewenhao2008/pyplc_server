# coding=utf-8
from flask import abort, jsonify

from web_server.ext import db
from web_server.models import YjStationInfo
from web_server.rest.parsers import station_parser, station_put_parser
from api_templete import ApiResource
from err import err_not_found
from response import rp_create, rp_delete, rp_modify


class StationResource(ApiResource):
    def __init__(self):
        self.args = station_parser.parse_args()
        super(StationResource, self).__init__()

    def search(self):
        station_id = self.args['id']

        station_name = self.args['station_name']

        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = YjStationInfo.query

        if station_id:
            query = query.filter_by(id=station_id)

        if station_name:
            query = query.filter_by(station_name=station_name)

        if page:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        return query

    def information(self, models):
        if not models:
            return err_not_found()

        info = []
        for m in models:
            data = dict()
            data['id'] = m.id
            data['station_name'] = m.station_name
            data['mac'] = m.mac
            data['ip'] = m.ip
            data['note'] = m.note
            data['id_num'] = m.id_num
            data['plc_count'] = m.plc_count
            data['ten_id'] = m.ten_id
            data['item_id'] = m.item_id
            data['modification'] = m.modification
            data['phone'] = m.phone
            data['version'] = m.version
            info.append(data)

        response = jsonify({'ok': 1, "data": info})
        response.status_code = 200

        return response

    def put(self):
        args = station_put_parser.parse_args()

        model_id = args['id']

        if model_id:
            model = YjStationInfo.query.get(model_id)

            if not model:
                return err_not_found()

            if args['station_name'] is not None:
                model.station_name = args['station_name']

            if args['mac'] is not None:
                model.mac = args['mac']

            if args['ip'] is not None:
                model.ip = args['ip']

            if args['note'] is not None:
                model.note = args['note']

            if args['id_num'] is not None:
                model.id_num = args['id_num']

            if args['plc_count'] is not None:
                model.plc_count = args['plc_count']

            if args['ten_id'] is not None:
                model.ten_id = args['ten_id']

            if args['item_id'] is not None:
                model.item_id = args['item_id']

            if args['modification'] is not None:
                model.modification = args['modification']

            if args['phone'] is not None:
                model.phone = args['phone']

            if args['version'] is not None:
                model.version = args['version']

            db.session.add(model)
            db.session.commit()

            return rp_modify()

        else:
            model = YjStationInfo(
                station_name=args['station_name'],
                mac=args['mac'],
                ip=args['ip'],
                note=args['note'],
                id_num=args['id_num'],
                plc_count=args['plc_count'],
                ten_id=args['ten_id'],
                item_id=args['item_id'],
                modification=args['modification'],
                phone=args['phone'],
                version=args['version']
            )
            db.session.add(model)
            db.session.commit()

            return rp_create()
