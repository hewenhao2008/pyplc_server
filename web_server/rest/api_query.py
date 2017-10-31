# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, QueryGroup, YjVariableInfo
from web_server.rest.parsers import query_parser, query_put_parser
from web_server.utils.err import err_not_found, err_not_contain
from web_server.utils.response import rp_create, rp_modify, rp_delete, rp_delete_ration, rp_get


class QueryResource(ApiResource):
    def __init__(self):
        self.args = query_parser.parse_args()
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10
        super(QueryResource, self).__init__()

    def search(self):

        model_id = self.args['id']

        name = self.args['name']

        min_time = self.args['min_time']
        max_time = self.args['max_time']
        order_time = self.args['order_time']
        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = QueryGroup.query

        if model_id is not None:
            query = query.filter_by(id=model_id)

        if name is not None:
            query = query.filter_by(name=name)

        if min_time is not None:
            query = query.filter(QueryGroup.time > min_time)

        if max_time is not None:
            query = query.filter(QueryGroup.time < max_time)

        if order_time is not None:
            query = query.order_by(QueryGroup.time.desc())

        if limit is not None:
            query = query.limit(limit)

        if self.page is not None:
            pagination = query.paginate(self.page, self.per_page, False)
            self.total = pagination.total
            self.per_page = pagination.per_page
            self.pages = pagination.pages
            query = pagination.items

        else:
            query = query.all()

        print query

        return query

    def information(self, models):

        info = []
        for m in models:
            print(m)
            data = dict()
            data['id'] = m.id
            data['name'] = m.name

            variable_list = [
                dict(
                    id=v.id,
                    variable_name=v.variable_name
                )
                for v in m.vars
            ]

            data['variables'] = variable_list

            info.append(data)

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total, self.per_page)

        return rp

    def put(self):
        args = query_put_parser.parse_args()

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

    def delete(self):

        models = self.search()

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
            count = len(models)

            for m in models:
                db.session.delete(m)
            db.session.commit()

        return rp_delete(count)

    def patch(self):
        args = query_put_parser.parse_args()

        model_id = args['id']

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
