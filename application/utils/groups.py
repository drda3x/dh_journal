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

    return Groups.objects.filter(
        Q(teacher_leader=user) | Q(teacher_follower=user)
    ).values()


def get_group_detail(group_id):

    u"""
    Получить детальную информацию о группе
    """

    group = Groups.objects.get(pk=group_id)
    students = get_group_students_list(group)
    cl = group.get_calendar()
    return {
        'id': group.id,
        'name': group.name,
        'start_date': group.start_date,
        'students': students
    }


def get_group_students_list(group):

    u"""
    Получить список учеников из группы
    """

    if not isinstance(group, Groups):
        raise TypeError('Expected Groups instance!')

    return Students.objects.filter(
        pk__in=Passes.objects.filter(group=group).values('student_id')
    )


def get_teacher_students_list(teacher):

    u"""
    Получить список учеников конкретного преподавателя
    """

    if not isinstance(teacher, User):
        raise TypeError('Expected User instance!')

    res = []

    for group in Groups.objects.filter(Q(teacher_leader=teacher) | Q(teacher_follower=teacher)):

        res += filter(
            lambda elem: elem not in res,
            __get_group_students_list(group)
        )

    return res