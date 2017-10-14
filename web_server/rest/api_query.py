# coding=utf-8
import datetime
import time

from flask import abort, jsonify

from web_server.models import db, QueryGroup, YjVariableInfo, Value
from web_server.rest.parsers import query_parser, query_put_parser
from api_templete import ApiResource
from err import err_not_found, err_not_contain
from response import rp_create, rp_delete, rp_modify, rp_delete_ration


class QueryResource(ApiResource):
    def __init__(self):
        self.args = query_parser.parse_args()
        super(QueryResource, self).__init__()

    def search(self, model_id=None):

        if not model_id:
            model_id = self.args['id']

        name = self.args['name']

        min_time = self.args['min_time']
        max_time = self.args['max_time']
        order_time = self.args['order_time']
        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = QueryGroup.query

        if model_id:
            query = query.filter_by(id=model_id)

        if name:
            query = query.filter_by(name=name)

        if min_time:
            query = query.filter(QueryGroup.time > min_time)

        if max_time:
            query = query.filter(QueryGroup.time < max_time)

        if order_time:
            query = query.order_by(QueryGroup.time.desc())

        if limit:
            query = query.limit(limit)

        if page:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        # print query

        return query

    def information(self, models):
        if not models:
            return err_not_found()

        info = []
        for m in models:
            data = dict()
            data['id'] = m.id
            data['name'] = m.name

            variable_list = [
                dict(
                    var_id=v.id,
                    var_name=v.variable_name
                )
                for v in m.vars
            ]

            data['variable'] = variable_list

            info.append(data)

        response = jsonify({"ok": 1, "data": info})

        return response

    def put(self, model_id=None):
        args = query_put_parser.parse_args()

        if not model_id:
            model_id = args['id']

        if model_id:

            model = QueryGroup.query.get(model_id)

            if not model:
                return err_not_found()

            if args['name']:
                model.name = args['name']

            if args['variable_id']:
                var_models = YjVariableInfo.query.filter(YjVariableInfo.id.in_(args['variable_id'])).all()
                # 添加关系，使用并集操作防止重复添加
                model.vars = list(set(model.vars).union(set(var_models)))

            db.session.add(model)
            db.session.commit()
            return rp_modify()

        else:

            if args['variable_id']:
                var_models = YjVariableInfo.query.filter(YjVariableInfo.id.in_(args['variable_id'])).all()
            else:
                var_models = []

            model = QueryGroup(
                name=args['name'],
                vars=var_models
            )

            db.session.add(model)
            db.session.commit()
            return rp_create()

    def delete(self, model_id=None):

        models = self.search(model_id)
        count = len(models)

        if not models:
            return err_not_found()

        if self.args['variable_id']:
            for m in models:
                delete_models = YjVariableInfo.query.filter(YjVariableInfo.id.in_(self.args['variable_id']))
                for var in delete_models:
                    try:
                        m.vars.remove(var)
                    except ValueError:
                        return err_not_contain()
            db.session.commit()
            return rp_delete_ration()
        else:
            for m in models:
                db.session.delete(m)
            db.session.commit()

        return rp_delete(count)
