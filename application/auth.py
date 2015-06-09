# -*- coding:utf-8 -*-

from django.contrib import auth


def check_auth(request):

    if request.user.is_authenticated():
        return request.user

    username = request.POST['username'] if 'username' in request.POST else None
    password = request.POST['password'] if 'password' in request.POST else None
    user = auth.authenticate(username=username, password=password)

    if user and user.is_active:
        if 'remember' in request.POST:
            auth.login(request, user)
        return user

    else:
        return None