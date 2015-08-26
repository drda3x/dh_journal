# -*- coding:utf-8 -*-

from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from application.models import User
from django.http.response import HttpResponseNotAllowed


def check_auth(request):

    try:
        user = User.objects.get(pk=request.session.get('uid', None))
    except Exception:
        user = None

    if user and user.is_authenticated():
        return user

    username = request.POST['username'] if 'username' in request.POST else None
    password = request.POST['password'] if 'password' in request.POST else None
    user = auth.authenticate(username=username, password=password)

    if user and user.is_active:
        if 'remember' in request.POST:
            auth.login(request, user)

        request.session = SessionStore()
        request.session['uid'] = user.id

        return user

    else:
        return None


def auth_decorator(func):

    def process(request):
        request.user = check_auth(request)

        if request.user:
            return func(request)

        else:
            return HttpResponseNotAllowed('User does not authorized. Please logout and login again')

    return process


def log_out(request):
    request.session.delete()
    auth.logout(request)