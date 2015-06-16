# -*- coding:utf-8 -*-

import datetime

from django.db.models import Q
from django.contrib.auth.models import User

from application.models import Groups, Students, Passes, Lessons, GroupList
from application.utils.date_api import get_count_of_weekdays_per_interval


def get_groups_list(user):

    u"""
    Получить список групп для конкретного пользоваетля
    """

    if not isinstance(user, User):
        return None

    return Groups.objects.filter(
        Q(teacher_leader=user) | Q(teacher_follower=user)
    ).values()


def get_group_detail(group_id, date_from, date_to):

    u"""
    Получить детальную информацию о группе
    """

    group = Groups.objects.get(pk=group_id)
    date = datetime.date(2015, 6, 1)

    dates_count = get_count_of_weekdays_per_interval(
        group.days.all().values_list('name', flat=True),
        date_from,
        date_to
    )

    students = [
        {
            'person': s,
            'calendar': get_student_calendar(s, group, date, dates_count, '%d.%m.%Y')
        } for s in get_group_students_list(group)
    ]

    return {
        'id': group.id,
        'name': group.name,
        'start_date': group.start_date,
        'students': students,
        'calendar': map(lambda d: d.strftime('%d.%m.%Y'), group.get_calendar(date_from=date, count=dates_count))
    }


def get_group_students_list(group):

    u"""
    Получить список учеников из группы
    """

    if not isinstance(group, Groups):
        raise TypeError('Expected Groups instance!')

    return Students.objects.filter(
        pk__in=GroupList.objects.filter(group=group).values('student_id')
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


def get_student_calendar(student, group, from_date, lessons_count, form=None):

    u"""
    Получить календарь занятий для конкретного ученика и конкретной ргуппы
    """

    group_calendar = group.get_calendar(date_from=from_date, count=lessons_count)
    lessons = iter(Lessons.objects.filter(student=student, group=group, date__gte=from_date).order_by('date'))

    calendar = []

    try:
        c_lesson = lessons.next()

    except StopIteration:
        return [
            {
                'date': d if not form else d.strftime(form),
                'sign': False
            } for d in group_calendar
        ]

    no_lessons = False

    for c_date in group_calendar:

        if no_lessons or c_lesson.date > c_date:
            _pass = False

        else:
            _pass = True

            try:
                c_lesson = lessons.next()

            except StopIteration:
                no_lessons = True

        calendar.append({
            'date': c_date if not form else c_date.strftime(form),
            'pass': _pass,
            'sign': str(c_lesson.group_pass.one_lesson_prise) if c_lesson.presence_sign else '',
            'color': c_lesson.group_pass.color
        })

    return calendar