# coding=utf-8

from api_templete import ApiResource
from web_server.models import YjVariableInfo, YjGroupInfo, YjPLCInfo, Value, var_queries, db, QueryGroup
from web_server.rest.parsers import value_parser, value_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class ValueResource(ApiResource):
    def __init__(self):
        self.args = value_parser.parse_args()

        self.value_id = self.args['id']

        self.value = self.args['value']
        self.variable_id = self.args['variable_id']
        self.variable_name = self.args['variable_name']
        self.plc_id = self.args['plc_id']
        self.plc_name = self.args['plc_name']
        self.group_id = self.args['group_id']
        self.group_name = self.args['group_name']
        self.query_id = self.args['query_id']
        self.query_name = self.args['query_name']
        self.all_variable_id = self.args['all_variable_id']

        self.min_time = self.args['min_time']
        self.max_time = self.args['max_time']
        self.order_time = self.args['order_time']
        self.limit = self.args['limit']
        self.page = self.args['page']
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10

        super(ValueResource, self).__init__()

    def search(self):

        # query = db.session.query(db.distinct(Value.variable_id).label('variable_id'), Value)
        # query = db.session.query(Value, Value.variable_id)
        query = Value.query
        # query = db.session.query(Value.cls).group_by(Value.variable_id)

        # a = [a[0] for a in db.session.query(Value.variable_id).distinct()]
        # query = db.session.query(Value).filter(Value.variable_id.in_(a))
        if self.value_id is not None:
            query = query.filter_by(id=self.value_id)

        if self.variable_id is not None:
            query = query.filter(Value.variable_id.in_(self.variable_id))

        if self.all_variable_id is not None:
            sql = 'select yjvariableinfo.id from yjvariableinfo'
            models = db.engine.execute(sql).fetchall()
            variable_id = [model[0] for model in models]

        if self.variable_name is not None:
            query = query.join(YjVariableInfo).filter(YjVariableInfo.variable_name == self.variable_name)

        if self.plc_id is not None:
            query = query.join(YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.plc_id.in_(self.plc_id))

        if self.plc_name is not None:
            query = query.join(YjVariableInfo, YjGroupInfo, YjPLCInfo).filter(YjPLCInfo.plc_name == self.plc_name)

        if self.group_id is not None:
            query = query.join(YjVariableInfo).filter(YjVariableInfo.group_id.in_(self.group_id))

        if self.group_name is not None:
            query = query.join(YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.group_name == self.group_name)

        if self.query_id is not None:
            query = query.join(var_queries, var_queries.columns.query_id == self.query_id).filter(
                Value.variable_id.in_(var_queries.columns.variable_id))

        if self.query_name is not None:
            query = query.join(QueryGroup, QueryGroup.name == self.query_name). \
                join(var_queries, var_queries.columns.query_id == QueryGroup.id).filter(
                Value.variable_id.in_(var_queries.columns.variable_id))

        if self.value is not None:
            query = query.filter(Value.value == self.value)

        if self.min_time is not None:
            query = query.filter(Value.time > self.min_time)

        if self.max_time is not None:
            query = query.filter(Value.time < self.max_time)

        if self.order_time is not None:
            query = query.order_by(Value.time.desc())

        # if limit:
        #     q = q.limit(limit)

        # print(query)

        if self.page is not None:
            pagination = query.paginate(self.page, self.per_page, False)
            self.total = pagination.total
            self.per_page = pagination.per_page
            self.pages = pagination.pages
            query = pagination.items

        elif self.limit is not None:
            # time1 = time.time()

            query = [
                model
                for v in variable_id
                for model in
                query.filter(Value.variable_id == v).limit(self.limit).all()
            ]
            # time2 = time.time()
            # print time2 - time1
        else:
            query = query.all()

        return query

    def information(self, query):

        info = []
        for v in query:

            data = dict()
            data['id'] = v.id
            data['variable_id'] = v.variable_id
            data['value'] = v.value
            # print(v.value, type(v.value))
            data['time'] = v.time

            variable = v.yjvariableinfo
            if variable:
                data['variable_name'] = variable.variable_name
                group = variable.yjgroupinfo
            else:
                data['variable_name'] = None
                group = None

            if group:
                data['group_id'] = group.id
                data['group_name'] = group.group_name
                data['plc_id'] = group.plc_id
                plc = group.yjplcinfo
            else:
                data['group_id'] = None
                data['group_name'] = None
                data['plc_id'] = None
                plc = None

            if plc:
                data['plc_name'] = plc.plc_name
            else:
                data['plc_name'] = None

            info.append(data)

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total)

        return rp

    def put(self):
        args = value_put_parser.parse_args()

        model = Value(
            variable_id=args['variable_id'],
            value=args['value'],
            time=args['time']
        )

        db.session.add(model)
        db.session.commit()

        return rp_create()

    def patch(self):
        args = value_put_parser.parse_args()

        model_id = args['id']

        model = Value.query.get(model_id)

        if not model:
            return err_not_found()

        if args['variable_id']:
            model.variable_id = args['variable_id']

        if args['value']:
            model.value = args['value']

        if args['time']:
            model.time = args['time']

        db.session.add(model)
        db.session.commit()

        return rp_modify()
