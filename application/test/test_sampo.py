# -*- coding: utf-8 -*-

from datetime import datetime
from django.test import TestCase
from tests_settings import SampoAdminTestSetting

from application.models import SampoPasses, SampoPassUsage, SampoPayments


class SampoTest(SampoAdminTestSetting, TestCase):
    """
    Тестирование функционала САМПО
    """

    def test_add(self):
        # Добавление оплаты
        add_responce = self.client.get('/sampo', {'action': 'add', 'data': '{"info":{"time":"17:34","count":"200"}}',
                                                  'type': 'cash-add'})
        self.assertEqual(add_responce.status_code, 200)

    def test_write_off(self):
        # Добавление списания
        wrt_responce = self.client.get('/sampo', {'action': 'add',
                                                  'data': '{"info":{"time":"18:22","count":"500","reason":"Тестовое списание"}}',
                                                  'type': 'cash-wrt'})
        self.assertEqual(wrt_responce.status_code, 200)

    def test_add_pass(self):
        # Добавление абонемента
        ass_pass_responce = self.client.get('/sampo', {'action': 'add',
            'data': '{"info":{"time":"18:33","surname":"test","name":"test","count":"1000"}}', 'type': 'pass'})
        self.assertEqual(ass_pass_responce.status_code, 200)

    def test_sampo_state_change(self):
        # Проставление отметки о присутствии
        payment = SampoPayments(date=datetime.now(), staff_id=4, people_count=0, money=1000)
        payment.save()

        _pass = SampoPasses(name='test', surname='test', payment=payment)
        _pass.save()

        check = self.client.get('/sampo', {'action': 'check', 'pid': _pass.pk, 'time': '10:00'})
        self.assertEqual(check.status_code, 200)

        uncheck = self.client.get('/sampo', {'action': 'uncheck', 'pid': _pass.pk, 'time': '10:00'})
        self.assertEqual(uncheck.status_code, 200)

    def test_sampo_del(self):
        # Удаление записей
        payment = SampoPayments(date=datetime.now(), staff_id=4, people_count=0, money=200)
        payment.save()

        pass_payment = SampoPayments(date=datetime.now(), staff_id=4, people_count=0, money=1000)
        pass_payment.save()

        _pass = SampoPasses(name='test', surname='test', payment=pass_payment)
        _pass.save()

        del_payment = self.client.get('/sampo', {'action': 'del', 'pid': 'p%d' % payment.pk})
        self.assertEqual(del_payment.status_code, 200)

        del_pass = self.client.get('/sampo', {'action': 'del', 'pid': 'p%d' % pass_payment.pk})
        self.assertEqual(del_pass.status_code, 200)
