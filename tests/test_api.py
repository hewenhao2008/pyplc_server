# coding=u8
import unittest

import pytest
import requests
from requests import get, post, put, delete, patch

# HOST = 'http://1.yakumo.applinzi.com'
HOST = 'http://127.0.0.1:11000'

GET_CODE = 200
POST_CODE = 200
PUT_CODE = 201
PATCH_CODE = 200
DELETE_CODE = 200
NOT_FOUND_CODE = 400


class TestApi(object):
    def api_test(self, path, test_key, test_value, patch_value):
        path = path
        url = HOST + path
        test_key = test_key
        test_value = test_value

        put_data = {
            test_key: test_value
        }
        rp = put(url, json=put_data)
        assert rp.status_code == PUT_CODE

        rp = get(url)
        assert rp.status_code == GET_CODE

        rp = post(url, json=put_data)
        assert rp.status_code == POST_CODE
        post_data = rp.json()['data'][0]
        model_id = post_data['id']
        print(post_data)
        assert str(post_data[test_key]) == str(put_data[test_key])

        patch_data = {
            'id': model_id,
            test_key: patch_value
        }
        rp = patch(url, json=patch_data)
        assert rp.status_code == PATCH_CODE

        rp = post(url, patch_data)
        post_data_2 = rp.json()['data'][0]
        assert str(post_data_2[test_key]) == str(patch_data[test_key])

        rp = delete(url, json=patch_data)
        assert rp.status_code == DELETE_CODE

    # @pytest.mark.skip
    def test_api_station(self):
        path = '/api/station'
        test_key = 'station_name'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_plc(self):
        path = '/api/plc'
        test_key = 'plc_name'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_group(self):
        path = '/api/group'
        test_key = 'group_name'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_variable(self):
        path = '/api/variable'
        test_key = 'variable_name'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_value(self):
        path = '/api/value'
        test_key = 'value'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_alarm(self):
        path = '/api/alarm'
        test_key = 'time'
        self.api_test(path, test_key, test_value=1, patch_value=2)

    # @pytest.mark.skip
    def test_api_alarm_info(self):
        path = '/api/alarm_info'
        test_key = 'note'
        self.api_test(path, test_key, test_value='pytest', patch_value='patch')

    # @pytest.mark.skip
    def test_api_station_alarm(self):
        path = '/api/station_alarm'
        test_key = 'code'
        self.api_test(path, test_key, test_value=999, patch_value=9999)

    # @pytest.mark.skip
    def test_api_alarm_log(self):
        path = '/api/alarm_log'
        test_key = 'status'
        self.api_test(path, test_key, test_value=999, patch_value=9999)

    # @pytest.mark.skip
    def test_api_plc_alarm(self):
        path = '/api/plc_alarm'
        test_key = 'id_num'
        self.api_test(path, test_key, test_value='pytest', patch_value='pytest')

    # @pytest.mark.skip
    def test_api_query(self):
        path = '/api/query'
        test_key = 'name'
        self.api_test(path, test_key, test_value='pytest', patch_value='pytest')

    def test_api_user(self):
        pass

    def test_api_param(self):
        pass

    # @pytest.mark.skip
    def test_api_query_relation(self):
        path = '/api/query'
        test_key = 'name'
        test_value = 'relation'
        relation_key = 'variables'
        relation_request_key = 'variable_id'
        url = HOST + path

        # 创建外链数据
        relation_path = '/api/variable'
        relation_test_key = 'variable_name'
        relation_url = HOST + relation_path
        # 外链数据内容
        put_data = {
            relation_test_key: 'relation'
        }

        # 清空残留数据

        # 删除操作
        delete_data = {
            test_key: test_value
        }
        delete(url, json=delete_data)
        delete(relation_url, json=delete_data)

        post_data = {
            test_key: test_value
        }

        # post检查是否删除干净
        rp = post(url, json=post_data)
        assert rp.status_code == POST_CODE
        assert rp.json()['count'] == 0

        rp = post(relation_url, json=post_data)
        assert rp.status_code == POST_CODE
        assert rp.json()['count'] == 0

        # 开始本次测试

        # put请求，创建数据
        relation_model_num = 4
        for i in range(relation_model_num):
            rp = put(relation_url, json=put_data)
            assert rp.status_code == PUT_CODE

        # post请求，获取创建的数据
        rp = post(relation_url, json=put_data)
        assert rp.status_code == POST_CODE

        # 获得创建数据的id
        relation_model_id = [model['id'] for model in rp.json()['data']]

        # 检查PUT方法

        # 创建测试接口数据，外链数据id为刚才创建的前两条数据
        put_data = {
            test_key: 'relation',
            relation_request_key: relation_model_id[:relation_model_num / 2]

        }

        rp = put(url, json=put_data)
        assert rp.status_code == PUT_CODE

        # post请求，获取创建的数据

        rp = post(url, json=post_data)
        assert rp.status_code == POST_CODE

        # 获取接口数据信息
        model = rp.json()['data'][0]
        model_id = model['id']

        # 检查数据中是否包含了足够的外链数据
        variables = rp.json()['data'][0][relation_key]
        assert len(variables) == relation_model_num / 2

        # 检查外链数据是否正确
        for i in range(relation_model_num / 2):
            assert variables[i]['id'] == relation_model_id[i]

        # 检查PATCH方法，添加关系

        patch_data = {
            'id': model_id,
            relation_request_key: relation_model_id[relation_model_num / 2:]
        }
        rp = patch(url, json=patch_data)
        assert rp.status_code == PATCH_CODE

        rp = post(url, post_data)
        # 获取外链数据
        variables = rp.json()['data'][0][relation_key]
        assert len(variables) == relation_model_num
        for i in range(relation_model_num):
            assert variables[i]['id'] == relation_model_id[i]

        # 检查DELETE方法，删除关系

        # 删除一条数据
        for i in range(relation_model_num - 1):
            delete_data = {
                'id': model_id,
                relation_request_key: relation_model_id[i]
            }
            rp = delete(url, json=delete_data)
            assert rp.status_code == DELETE_CODE

            rp = post(url, json=post_data)
            assert rp.status_code == POST_CODE

            variables = rp.json()['data'][0][relation_key]
            assert len(variables) == relation_model_num - i - 1
            assert variables[0]['id'] == relation_model_id[i + 1]

        # 再删除一条数据
        delete_data = {
            'id': model_id,
            relation_request_key: relation_model_id[relation_model_num - 1]
        }
        rp = delete(url, json=delete_data)
        assert rp.status_code == DELETE_CODE

        post_data = {
            test_key: 'relation'
        }
        rp = post(url, json=post_data)
        assert rp.status_code == POST_CODE

        variables = rp.json()['data'][0][relation_key]
        assert len(variables) == 0


if __name__ == '__main__':
    unittest.main()
