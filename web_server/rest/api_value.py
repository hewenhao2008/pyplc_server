# coding=utf-8

from api_templete import ApiResource
from web_server.models import YjVariableInfo, YjGroupInfo, YjPLCInfo, Value, var_queries, db, QueryGroup
from web_server.rest.parsers import value_parser, value_put_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class ValueResource(ApiResource):
    def __init__(self):
        self.args = value_parser.parse_args()
        super(ValueResource, self).__init__()

    def search(self):

        value_id = self.args['id']

        value = self.args['value']
        variable_id = self.args['variable_id']
        variable_name = self.args['variable_name']
        plc_id = self.args['plc_id']
        plc_name = self.args['plc_name']
        group_id = self.args['group_id']
        group_name = self.args['group_name']
        query_id = self.args['query_id']
        query_name = self.args['query_name']
        all_variable_id = self.args['all_variable_id']

        min_time = self.args['min_time']
        max_time = self.args['max_time']
        order_time = self.args['order_time']
        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        # query = db.session.query(db.distinct(Value.variable_id).label('variable_id'), Value)
        # query = db.session.query(Value, Value.variable_id)
        query = Value.query
        # query = db.session.query(Value.cls).group_by(Value.variable_id)

        # a = [a[0] for a in db.session.query(Value.variable_id).distinct()]
        # query = db.session.query(Value).filter(Value.variable_id.in_(a))
        if value_id is not None:
            query = query.filter_by(id=value_id)

        if variable_id is not None:
            query = query.filter(Value.variable_id.in_(variable_id))

        if all_variable_id is not None:
            sql = 'select yjvariableinfo.id from yjvariableinfo'
            models = db.engine.execute(sql).fetchall()
            variable_id = [model[0] for model in models]

        if variable_name is not None:
            query = query.join(YjVariableInfo).filter(YjVariableInfo.variable_name == variable_name)

        if plc_id is not None:
            query = query.join(YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.plc_id.in_(plc_id))

        if plc_name is not None:
            query = query.join(YjVariableInfo, YjGroupInfo, YjPLCInfo).filter(YjPLCInfo.plc_name == plc_name)

        if group_id is not None:
            query = query.join(YjVariableInfo).filter(YjVariableInfo.group_id.in_(group_id))

        if group_name is not None:
            query = query.join(YjVariableInfo, YjGroupInfo).filter(YjGroupInfo.group_name == group_name)

        if query_id is not None:
            query = query.join(var_queries, var_queries.columns.query_id == query_id).filter(
                Value.variable_id.in_(var_queries.columns.variable_id))

        if query_name is not None:
            query = query.join(QueryGroup, QueryGroup.name == query_name). \
                join(var_queries, var_queries.columns.query_id == QueryGroup.id).filter(
                Value.variable_id.in_(var_queries.columns.variable_id))

        if value is not None:
            query = query.filter(Value.value == value)

        if min_time is not None:
            query = query.filter(Value.time > min_time)

        if max_time is not None:
            query = query.filter(Value.time < max_time)

        if order_time is not None:
            query = query.order_by(Value.time.desc())

        # if limit:
        #     q = q.limit(limit)

        # print(query)

        if page is not None:
            query = query.paginate(page, per_page, False).items
        elif limit is not None:
            # time1 = time.time()

            query = [
                model
                for v in variable_id
                for model in
                query.filter(Value.variable_id == v).limit(limit).all()
            ]
            # time2 = time.time()
            # print time2 - time1
        else:
            query = query.all()

        # print query

        return query

    def information(self, value):

        info = []
        for v in value:

            data = dict()
            data['id'] = v.id
            data['variable_id'] = v.variable_id
            data['value'] = v.value
            print(v.value, type(v.value))
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
        rp = rp_get(info)

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
