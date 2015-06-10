# -*- coding:utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import User

from application.models import Groups, Students, Passes


def get_groups_list(user):
    u"""
    Получить список групп для конкретного пользоваетля
    """

    if not isinstance(user, User):
        return None

    groups = Groups.objects.filter(
        Q(teacher_leader=user) | Q(teacher_follower=user)
    ).values()

    return groups


def get_group_detail(group_id):
    group = Groups.objects.get(pk=group_id)


def get_group_students_list(group):
    if not isinstance(group, Groups):
        raise TypeError('Expected Groups instance!')

    return Students.objects.filter()

def get_teacher_students_list():
    pass