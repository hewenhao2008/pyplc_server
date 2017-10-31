# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, Parameter, Value
from web_server.rest.parsers import param_parser
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_create, rp_modify, rp_get


class ParameterResource(ApiResource):
    def __init__(self):
        self.args = param_parser.parse_args()
        super(ParameterResource, self).__init__()
        self.query = Parameter.query

        self.model_id = self.args['id']

        self.param_name = self.args['param_name']
        self.variable_id = self.args['variable_id']
        self.unit = self.args['unit']

        self.limit = self.args['limit']
        self.total = None
        self.page = self.args['page'] if self.args['page'] else 1
        self.pages = None
        self.per_page = self.args['per_page'] if self.args['per_page'] else 10

    def search(self):

        if self.model_id:
            self.query = self.query.filter_by(id=self.model_id)

        if self.param_name:
            self.query = self.query.filter_by(param_name=self.param_name)

        if self.variable_id:
            self.query = self.query.filter_by(variable_id=self.variable_id)

        if self.unit:
            self.query = self.query.filter_by(unit=self.unit)

        if self.limit:
            self.query = self.query.limit(self.limit)

        if self.page:
            self.query = self.query.paginate(self.page, self.per_page, False).items
        else:
            self.query = self.query.all()

        return self.query

    def information(self, models):
        info = [
            dict(
                id=m.id,
                param_name=m.param_name,
                variable_id=m.variable_id,
                unit=m.unit,
            )
            for m in models
        ]

        for m in info:
            try:
                value = db.session.query(Value.value).filter(
                    Value.variable_id == m['variable_id']).order_by(Value.time.desc()).first()[0]
            except TypeError:
                value = None
            m['value'] = value

        # 返回json数据
        rp = rp_get(info, self.page, self.pages, self.total, self.per_page)

        return rp

    def put(self):

        model = Parameter(
            variable_id=self.variable_id,
            param_name=self.param_name,
            unit=self.unit
        )
        db.session.add(model)
        db.session.commit()
        return rp_create()

    def patch(self):

        model = Parameter.query.get(self.model_id)

        if not model:
            return err_not_found()

        if self.param_name:
            model.param_name = self.param_name

        if self.variable_id:
            model.variable_id = self.variable_id

        if self.unit:
            model.unit = self.unit

        db.session.add(model)
        db.session.commit()
        return rp_modify()
