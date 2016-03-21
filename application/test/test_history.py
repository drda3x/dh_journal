# -*- coding:utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class HistoryTestCase(TestCase):
    """
    Доступ к странице истории
    """

    client = Client()

    def test_admin_access(self):
        self.client.post('/login', {'username': 'test_admin', 'password': 'test_admin'})

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)

    def test_teacher_access(self):
        self.client.post('/login', {'username': 'test_user', 'password': 'test_user'})

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)

    def test_sampo_admin_access(self):
        log_in_responce = self.client.post('/login', {'username': 'test_sampo', 'password': 'test_sampo'})

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
