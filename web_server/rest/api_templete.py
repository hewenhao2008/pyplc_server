# coding=utf-8
import json
import time

from flask import request
from flask_restful import Resource, abort, wraps

from web_server.models import db, User, InterfaceLog, serialize
from web_server.utils.err import err_not_found
from web_server.utils.response import rp_delete


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        token = request.json.get('token')
        acct = User.verify_auth_token(token)

        if acct:
            return func(*args, **kwargs)

        abort(401, msg='用户验证错误', ok=0)

    return wrapper


class ApiResource(Resource):
    # method_decorators = [authenticate]
    def __init__(self):
        # print(request, request.json, 'abcd')

        self.user = None
        # self.user = self.verify()
        self.new_id = None
        self.query = None
        pass

    # def __del__(self):
    #     try:
    #         self.interface_log(self.user, self.query, self.new_id)
    #     except AttributeError:
    #         pass

    def verify(self):
        token = self.args['token']
        user = User.verify_auth_token(token)

        if not user:
            abort(401, msg='用户验证错误', ok=0)

        return user

    @staticmethod
    def interface_log(user, query, new_id):
        print 'a'
        current_time = int(time.time())
        param = request.json
        del param['token']

        # if not False:
        if not request.method == 'POST' or request.method == 'GET':

            old_data = json.dumps(
                [serialize(m) for m in query]
            )
        else:
            old_data = None
        log = InterfaceLog(
            username=user.username,
            host_url=request.path,
            method=request.method.lower(),
            time=current_time,
            param=json.dumps(param),
            old_data=old_data,
            endpoint=request.endpoint,
            new_data_id=new_id
        )
        db.session.add(log)
        db.session.commit()

    def search(self):
        pass

    def information(self, models):
        pass

    def get(self):

        # time1 = time.time()
        models = self.search()

        rp = self.information(models)
        # time2 = time.time()
        # print time2 - time1

        return rp

    def post(self):

        models = self.search()

        rp = self.information(models)

        return rp

    def put(self):
        pass

    def patch(self):
        pass

    def delete(self):

        models = self.search()
        count = len(models)

        if not models:
            return err_not_found()

        for m in models:
            db.session.delete(m)
        db.session.commit()

        return rp_delete(count)
