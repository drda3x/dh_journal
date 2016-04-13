#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from tests_settings import AdminTestSetting, TeacherTestSetting
from utils import *


class AdminPrintTestCase(AdminTestSetting, TestCase):

    def setUp(self):
        super(AdminPrintTestCase, self).setUp()
        self.group = create_group()

    def test_print_group(self):
        response = self.client.get('/print', {'type': 'full', 'id': self.group.pk, 'date': '01012016', 'subtype': 'lessons'})
        self.assertEqual(response.status_code, 200)


class TeacherPrintTestCase(TeacherTestSetting, TestCase):

    def setUp(self):
        super(TeacherPrintTestCase, self).setUp()
        self.group = create_group()

    def test_print_group(self):
        response = self.client.get('/print', {'type': 'full', 'id': self.group.pk, 'date': '01012016', 'subtype': 'lessons'})
        self.assertEqual(response.status_code, 200)