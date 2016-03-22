# -*- coding:utf-8 -*-

from django.test import TestCase
from tests_settings import AdminTestSetting, TeacherTestSetting, SampoAdminTestSetting


class AdminHistoryTestCase(AdminTestSetting, TestCase):
    """
    Доступ к странице истории
    """

    def test_access(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)


class TeacherHistoryTestCase(TeacherTestSetting, TestCase):

    def test_access(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)


class SampoAdminHistoryTestCase(SampoAdminTestSetting, TestCase):

    def test_access(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
