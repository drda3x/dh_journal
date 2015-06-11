# -*- coding:utf-8 -*-

import datetime

from django.db.models import Q
from django.contrib.auth.models import User

from application.models import Groups, Students, Passes, Lessons


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
    date = datetime.date(2015, 7, 1)
    students = [
        {
            'person': s,
            'calendar': get_student_calendar(s, group, date)
        } for s in get_group_students_list(group)
    ]

    return {
        'id': group.id,
        'name': group.name,
        'start_date': group.start_date,
        'students': students,
        'calendar': map(lambda d: d.strftime('%d.%m'), group.get_calendar(date_to=date))
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
            get_group_students_list(group)
        )

    return res


def get_student_calendar(student, group, from_date):

    u"""
    Получить календарь занятий для конкретного ученика и конкретной ргуппы
    """

    group_calendar = group.get_calendar(date_to=from_date)
    lessons = iter(Lessons.objects.filter(student=student, group=group, date__gte=from_date).order_by('date'))

    calendar = []

    try:
        c_lesson = lessons.next()

    except StopIteration:
        return [
            {'date': d, 'sign': False} for d in group_calendar
        ]

    for c_date in group_calendar:

        if c_lesson.date > c_date:
            sign = False

        else:
            sign = True
            c_lesson = lessons.next()

        calendar.append({
            'date': c_date,
            'sign': sign
        })

    return calendar