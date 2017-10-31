# coding=utf-8

from api_templete import ApiResource
from web_server.ext import db
from web_server.models import YjPLCInfo, YjGroupInfo
from web_server.rest.parsers import group_parser, group_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class GroupResource(ApiResource):
    def __init__(self):
        self.args = group_parser.parse_args()
        super(GroupResource, self).__init__()

    def search(self):

        group_id = self.args['id']

        group_name = self.args['group_name']
        plc_id = self.args['plc_id']
        plc_name = self.args['plc_name']

        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = YjGroupInfo.query

        if group_id:
            query = query.filter_by(id=group_id)

        if group_name:
            query = query.filter_by(group_name=group_name)

        if plc_id:
            query = query.filter(YjGroupInfo.plc_id.in_(plc_id))

        if plc_name:
            query = query.join(YjPLCInfo, YjPLCInfo.plc_name == plc_name)

        if limit:
            query = query.limit(limit)

        if page:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        return query

    def information(self, group):

        info = []
        for g in group:

            data = dict()
            data['id'] = g.id
            data['group_name'] = g.group_name
            data['plc_id'] = g.plc_id
            data['upload_cycle'] = g.upload_cycle
            data['note'] = g.note
            data['ten_id'] = g.ten_id
            data['item_id'] = g.item_id
            data['upload'] = g.upload

            plc = g.yjplcinfo
            if plc:
                data['plc_name'] = plc.plc_name
            else:
                data['plc_name'] = None

            info.append(data)

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = group_put_parser.parse_args()

        model = YjGroupInfo(
            group_name=args['group_name'],
            plc_id=args['plc_id'],
            note=args['note'],
            upload_cycle=args['upload_cycle'],
            ten_id=args['ten_id'],
            item_id=args['item_id'],
            upload=args['upload']
        )

        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = group_put_parser.parse_args()

        model_id = args['id']

        model = YjGroupInfo.query.get(model_id)

        if not model:
            return err_not_found()

        if args['group_name']:
            model.group_name = args['group_name']

        if args['plc_id']:
            model.plc_id = args['plc_id']

        if args['note']:
            model.note = args['note']

        if args['upload_cycle']:
            model.upload_cycle = args['upload_cycle']

        if args['ten_id']:
            model.ten_id = args['ten_id']

        if args['item_id']:
            model.item_id = args['item_id']

        if args['upload']:
            model.upload = args['upload']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
