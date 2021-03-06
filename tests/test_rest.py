import unittest
import json

from requests import api
from users_api import today
from tests.helper import test_base_tornado, TestingHelper

from tornado.httpclient import AsyncHTTPClient
from datetime import datetime, timedelta

ID_TENANT = '8007dc9c-3e4d-450c-9f2c-18f312b21bdb'
import uuid


class TestUser(TestingHelper):

    def setUp(self):
        super().setUp()
        self.add_brand('Marlboro', 20, 200, 10)
        id_brand = self.last_result['id']

        self.api(None, 'POST', '/api/users/register',
                 body={
                     'id_tenant': ID_TENANT,
                     'username': 'user',
                     'password': '123ABCa.',
                     'brand_smoking': id_brand,
                     'average_per_day': 15,
                     'quit_date': str(datetime.today())
                 })

        self.assertEqual(200, self.last_code)
        self.id_session = self.last_result['id_session']

    def test_login_user(self):
        # self.flush_db_at_the_end = False
        self.api(None, 'POST', '/api/users/login',
                 body={
                     'id_tenant': ID_TENANT,
                     'username': 'user',
                     'password': '123ABCa.',
                 })
        self.assertEqual(200, self.last_code)
        self.assertTrue('status' in self.last_result and 'ok' in self.last_result['status'])
        self.assertTrue('id_session' in self.last_result)

    def test_try_login_user_with_invalid_password(self):
        self.api(None, 'POST', '/api/users/login',
                 body={
                     'id_tenant': ID_TENANT,
                     'username': 'user',
                     'password': '123ABCa!'}
                 )

        self.assertEqual(400, self.last_code)

    def test_protected_api_call(self):
        self.api(self.id_session, "GET", '/api/protected')
        self.assertTrue(200, self.last_code)
        print(self.last_result)

        self.api(None, "GET", '/api/protected')
        self.assertTrue(401, self.last_code)
        print(self.last_result)

        self.api(str(uuid.uuid4()), "GET", '/api/protected')
        self.assertTrue(401, self.last_code)
        print(self.last_result)

        # print(self.last_code)
        # print(self.last_result)


class TestRegistarUser(TestingHelper):
    def test_register_user(self):
        self.add_brand('Marlboro', 20, 200, 10)

        id_brand = self.last_result['id']
        self.api(None, 'POST', '/api/users/register',
                 body={
                     'id_tenant': ID_TENANT,
                     'username': 'user',
                     'password': '123ABCa.',
                     'brand_smoking': id_brand,
                     'average_per_day': 15,
                     'quit_date': str(datetime.today() - timedelta(5))
                 })
        self.assertEqual(200, self.last_code)

    def test_try_to_register_user_with_weak_password(self):
        self.api(None, 'POST', '/api/users/register',
                 body={
                     'id_tenant': ID_TENANT,
                     'username': 'user',
                     'password': '123',
                 })

        self.assertEqual(400, self.last_code)
        self.assertIn('id_error', self.last_result)
        self.assertEqual('PASSWORD_TO_WEAK', self.last_result['id_error'])


if __name__ == '__main__':
    unittest.main()
