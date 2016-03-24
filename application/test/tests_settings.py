# -*- coding:utf-8 -*-

from django.test.client import Client


class AdminTestSetting(object):
    fixtures = ['user.json']

    client = Client()

    def setUp(self):
        self.client.post('/login', {'username': 'test_admin', 'password': 'test_admin'})


class TeacherTestSetting(object):
    fixtures = ['user.json']

    client = Client()

    def setUp(self):
        self.client.post('/login', {'username': 'test_admin', 'password': 'test_admin'})


class SampoAdminTestSetting(object):
    fixtures = ['user.json']

    client = Client()

    def setUp(self):
        self.client.post('/login', {'username': 'test_admin', 'password': 'test_admin'})
