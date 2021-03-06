# coding=utf-8

from api_templete import ApiResource
from web_server.models import db, User, Role
from web_server.rest.parsers import user_parser
from web_server.utils.err import err_not_found, err_not_contain
from web_server.utils.response import rp_modify, rp_delete, rp_delete_ration, rp_get


class UserResource(ApiResource):
    def __init__(self):
        self.args = user_parser.parse_args()
        super(UserResource, self).__init__()

    def search(self):

        model_id = self.args['id']

        username = self.args['username']

        email = self.args['email']
        role = self.args['role']
        limit = self.args['limit']
        page = self.args['page']
        per_page = self.args['per_page'] if self.args['per_page'] else 10

        query = User.query

        if model_id:
            query = query.filter_by(id=model_id)

        if username:
            query = query.filter_by(username=username)

        if email:
            query = query.filter_by(email=email)

        if role:
            query = query.join(Role, Role.name.in_(role))

        if limit:
            query = query.limit(limit)

        print(query)

        if page:
            query = query.paginate(page, per_page, False).items
        else:
            query = query.all()

        print(query)

        # print query

        return query

    def information(self, models):

        info = [
            dict(
                username=m.username,
                email=m.email,
                login_count=m.login_count,
                last_login_ip=m.last_login_ip,
                last_login_time=m.last_login_time,
                role=[role.name for role in m.roles]
            )
            for m in models
        ]

        # 返回json数据
        rp = rp_get(info)

        return rp

    def put(self):
        args = user_parser.parse_args()

        model_id = args['id']

        if model_id:

            model = User.query.get(model_id)

            if not model:
                return err_not_found()

            if args['username']:
                model.username = args['username']

            if args['email']:
                model.email = args['email']

            if args['role']:
                role_models = Role.query.filter(Role.name.in_(args['role'])).all()
                model.roles += role_models

            db.session.add(model)
            db.session.commit()
            return rp_modify()

    def delete(self):

        models = self.search()
        count = len(models)

        if not models:
            return err_not_found()

        if self.args['role']:
            for m in models:
                delete_models = Role.query.filter(Role.name.in_(self.args['role']))
                for role in delete_models:
                    try:
                        m.roles.remove(role)
                    except ValueError:
                        return err_not_contain()
            db.session.commit()
            return rp_delete_ration()
        else:
            for m in models:
                db.session.delete(m)
            db.session.commit()

        return rp_delete(count)
