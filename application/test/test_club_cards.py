# -*- coding:utf-8 -*-

import datetime
from django.test import TestCase
from tests_settings import AdminTestSetting, TeacherTestSetting
from utils import *


class AdminClubCardTestCase(AdminTestSetting, TestCase):
    """
    Интерфейс клубных карт для админа
    """

    def setUp(self):
        super(AdminClubCardTestCase, self).setUp()
        self.group_pass = create_multipass()

    def test_access(self):
        response = self.client.get('/clubcards')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clubcards?id=%d' % self.group_pass.pk)
        self.assertEqual(response.status_code, 200)


class TeacherClubCardTestCase(TeacherTestSetting, TestCase):
    """
    Интерфейс клубных карт для преподавателя
    """

    def setUp(self):
        super(TeacherClubCardTestCase, self).setUp()
        self.group_pass = create_multipass()

    def test_access(self):
        response = self.client.get('/clubcards')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clubcards?id=%d' % self.group_pass.pk)
        self.assertEqual(response.status_code, 200)
