# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class LogInTest(TestCase):
    """
    Тест логина
    """
    fixtures = ['user.json']
    client = Client()

    def test_admin_login(self):
        # Попытка логина администратора
        log_in_responce = self.client.post('/login', {'username': 'test_admin', 'password': 'test_admin'})
        self.assertEqual(log_in_responce.status_code, 302)

        # Проверяем что после логина попали на главную страницу
        main_page_responce = self.client.get('/')
        self.assertEqual(main_page_responce.status_code, 200)

    def test_ordiarey_user(self):
        # Попытка логина обычного преподавателя
        log_in_responce = self.client.post('/login', {'username': 'test_user', 'password': 'test_user'})
        self.assertEqual(log_in_responce.status_code, 302)

        # Проверяем что после логина попали на главную страницу
        main_page_responce = self.client.get('/')
        self.assertEqual(main_page_responce.status_code, 200)

    def test_sampo_admin_user(self):
        # Попытка логина администратора сампо
        log_in_responce = self.client.post('/login', {'username': 'test_sampo', 'password': 'test_sampo'})
        self.assertEqual(log_in_responce.status_code, 302)

        # Проверяем что после логина попали на главную страницу
        main_page_responce = self.client.get('/sampo')
        self.assertEqual(main_page_responce.status_code, 200)

    def test_wrong_login(self):
        # Попытка авторизации с неверными данными
        wrong_login_response = self.client.post('/login', {'username': 'test_sampo', 'password': 'qwerty'})
        self.assertEqual(wrong_login_response.status_code, 200)
