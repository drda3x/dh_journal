# -*- coding:utf-8 -*-

import datetime
from django.test import TestCase
from tests_settings import AdminTestSetting, TeacherTestSetting

from application.models import Groups, GroupList, Students, Passes, PassTypes, DanceHalls


class AdminClubCardTestCase(AdminTestSetting, TestCase):
    """
    Интерфейс клубных карт для админа
    """

    def setUp(self):
        super(AdminClubCardTestCase, self).setUp()

        dh = DanceHalls(
            prise=1000
        )
        dh.save()

        pt = PassTypes(
            name='test_clubcard_pass',
            prise=1000,
            lessons=8,
            one_group_pass=False
        )
        pt.save()

        student = Students(
            first_name='fn',
            last_name='ln',
            phone='89261112233'
        )
        student.save()

        group = Groups(
            name='test_group',
            start_date=datetime.datetime(2016, 1, 1),
            teacher_leader_id=2,
            _days='4,5',
            _available_passes=str(pt.pk),
            dance_hall=dh
        )
        group.save()

        group_list = GroupList(
            group=group,
            student=student
        )
        group_list.save()

        self.group_pass = Passes(
            student=student,
            group=group,
            pass_type=pt
        )
        self.group_pass.save()

    def test_access(self):
        response = self.client.get('/clubcards')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clubcards?id=%d' % self.group_pass.pk)
        self.assertEqual(response.status_code, 200)


class TeacherClubCardTestCase(TeacherTestSetting, TestCase):
    """
    Интерфейс клубных карт для преподавателя
    """

    def test_access(self):
        response = self.client.get('/clubcards')
        self.assertEqual(response.status_code, 200)
