# -*- coding:utf-8 -*-

import datetime

from django.db.models import Q
from django.contrib.auth.models import User

from application.utils.passes import get_color_classes
from application.models import Groups, Students, Passes, Lessons, GroupList, Comments, CanceledLessons, Debts
from application.utils.date_api import get_count_of_weekdays_per_interval, get_week_days_names
from application.utils.passes import ORG_PASS_HTML_CLASS


def get_groups_list(user):

    u"""
    Получить список групп для конкретного пользоваетля
    """

    if not isinstance(user, User):
        return None

    return [
        {'id': g.id, 'name': g.name, 'days': ' '.join(g.days)}
        for g in Groups.objects.filter(
            Q(teacher_leader=user) | Q(teacher_follower=user),
            Q(is_opened=True)
        )
    ]


def get_group_detail(group_id, _date_from, date_to):

    u"""
    Получить детальную информацию о группе
    """

    group = Groups.objects.get(pk=group_id)

    gs_dt = datetime.datetime.combine(group.start_date, datetime.datetime.min.time())

    date_from = _date_from if gs_dt < _date_from else gs_dt

    dates_count = get_count_of_weekdays_per_interval(
        group.days,
        date_from,
        date_to
    )

    calendar = group.get_calendar(date_from=date_from, count=dates_count, clean=False)

    students = [
        {
            'person': s,
            'calendar': [get_student_lesson_status(s, group, dt) for dt in calendar],  #get_student_calendar(s, group, date_from, dates_count, '%d.%m.%Y'),
            'debt': check_debt(s, group),
            'pass_remaining': len(get_student_pass_remaining(s, group)),
            'multi_pass': (lambda x: {'id': x.id, 'lessons': x.lessons} if x else None)(get_student_multi_pass(s, date_from, date_to)),
            'last_comment': Comments.objects.filter(group=group, student=s).order_by('add_date').last()
        } for s in get_group_students_list(group)
    ]

    moneys = []
    money_total = {key: 0 for key in ('day_total', 'dance_hall')}

    for _day in calendar:
        buf = dict()

        if not _day['canceled']:
            qs = Lessons.objects.filter(group=group, date=_day['date'])

            flag = qs.exclude(status__in=(Lessons.STATUSES['not_processed'], Lessons.STATUSES['moved'])).exists()

            buf['day_total'] = reduce(lambda _sum, l: _sum + l.prise(), qs.exclude(status=Lessons.STATUSES['moved']), 0) if flag else ''
            buf['dance_hall'] = group.dance_hall.prise if flag else ''
            buf['club'] = round((buf['day_total'] - buf['dance_hall']) * 0.3, 0) if flag else ''
            buf['balance'] = round(buf['day_total'] - buf['dance_hall'] - abs(buf['club']), 0) if flag else ''
            buf['half_balance'] = round(buf['balance'] / 2, 1) if isinstance(buf['balance'], (float, int)) else ''
            buf['date'] = _day if flag else ''
            buf['canceled'] = False

            for key in money_total.iterkeys():
                money_total[key] += (buf[key] if isinstance(buf[key], (int, float)) else 0)

        else:
            buf['day_total'] = ''
            buf['dance_hall'] = ''
            buf['club'] = ''
            buf['balance'] = ''
            buf['half_balance'] = ''
            buf['date'] = ''
            buf['canceled'] = True

        moneys.append(buf)

    money_total['club'] = round((money_total['day_total'] - money_total['dance_hall']) * 0.3, 0)
    money_total['balance'] = round(money_total['day_total'] - money_total['dance_hall'] - abs(money_total['club']), 0)
    money_total['half_balance'] = round(money_total['balance'] / 2, 1)

    # money = dict()
    # money['dance_hall'] = group.dance_hall.prise
    # money['total'] = reduce(lambda _sum, l: _sum + l.prise(), Lessons.objects.filter(group=group, date__range=[date_from, date_to]).exclude(status=Lessons.STATUSES['moved']), 0)
    # money['club'] = round((money['total'] - money['dance_hall']) * 0.3, 0)
    # money['balance'] = round(money['total'] - money['dance_hall'] - money['club'], 0)

    def to_iso(elem):
        elem['date'] = elem['date'].strftime('%d.%m.%Y')

        return elem

    return {
        'id': group.id,
        'name': group.name,
        'days': group.days,
        'start_date': group.start_date,
        'students': students,
        'last_lesson': group.last_lesson,
        'calendar': map(to_iso, calendar),
        'moneys': moneys,
        'money_total': money_total
    }


def check_debt(student, group):

    u'''
    Проверить наличие долгов у студента
    :param student: models.Student
    :param group: models.Group
    :return: models.Debt | None
    '''

    try:
        return Debts.objects.get(student=student, group=group)

    except Debts.DoesNotExist:
        return None


def get_student_pass_remaining(student, group):
    passes = Passes.objects.filter(student=student, group=group)
    return [l for p in passes for l in Lessons.objects.filter(group_pass=p, status=Lessons.STATUSES['not_processed'])]


def get_student_multi_pass(student, date_from, date_to):
    try:
        p = Passes.objects.get(
            pass_type__one_group_pass=False,
            start_date__lte=date_to,
            end_date__gte=date_from,
            student=student,
            lessons__gt=0
        )

        return p

    except Passes.DoesNotExist:
        return None


def get_group_students_list(group):

    u"""
    Получить список учеников из группы
    """

    if not isinstance(group, Groups):
        raise TypeError('Expected Groups instance!')

    return Students.objects.filter(
        pk__in=GroupList.objects.filter(group=group, active=True).values('student_id'),
        is_deleted=False
    ).order_by('last_name', 'first_name')


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


def get_student_lesson_status(student, group, _date):

    date = _date['date']

    if _date['canceled']:
        return {
            'pass': False,
            'color': '',
            'sign': '',
            'attended': False,
            'canceled': True
        }

    try:
        lesson = Lessons.objects.get(student=student, group=group, date=date)

        html_color_classes = {
            key: val for val, key in get_color_classes()
        }

        buf = {
            'pass': True,
            'sign': '' if lesson.status == Lessons.STATUSES['moved'] else (lesson.prise() if lesson.status == Lessons.STATUSES['attended'] else lesson.prise() * -1) if not lesson.status == Lessons.STATUSES['not_processed'] else '',
            'attended': lesson.status == Lessons.STATUSES['attended']
        }

        if not lesson.status == Lessons.STATUSES['moved']:

            if not student.org or not lesson.group_pass.pass_type.one_group_pass or lesson.group_pass.pass_type.lessons == 1:
                    buf['color'] = html_color_classes[lesson.group_pass.color]
            else:
                buf['color'] = ORG_PASS_HTML_CLASS

        buf['canceled'] = False

        return buf

    except Lessons.DoesNotExist:
        return {
            'pass': False,
            'color': '',
            'sign': '',
            'attended': False,
            'canceled': False
        }


# def get_student_calendar(student, group, from_date, lessons_count, form=None):
#
#     u"""
#     Получить календарь занятий для конкретного ученика и конкретной ргуппы
#     """
#
#     html_color_classes = {
#         key: val for val, key in get_color_classes()
#     }
#
#     group_calendar = group.get_calendar(date_from=from_date, count=lessons_count)
#     lessons = Lessons.objects.filter(student=student, group=group, date__gte=from_date).order_by('date')
#     lessons_itr = iter(lessons)
#
#     calendar = []
#
#     try:
#         c_lesson = lessons_itr.next()
#
#     except StopIteration:
#         return [
#             {
#                 'date': d if not form else d.strftime(form),
#                 'sign': ''
#             } for d in group_calendar
#         ]
#
#     no_lessons = False
#
#     for c_date in group_calendar:
#
#         buf = {
#             'date': c_date if not form else c_date.strftime(form)
#         }
#
#         if no_lessons or c_lesson.date > c_date.date():
#             buf['pass'] = False
#             buf['color'] = None
#             buf['sign'] = ''
#
#         else:
#             buf['pass'] = True
#             buf['sign'] = c_lesson.rus if not c_lesson.status == Lessons.STATUSES['not_processed'] and c_lesson.date == c_date.date() else ''
#
#             if not student.org or not c_lesson.group_pass.pass_type.one_group_pass or c_lesson.group_pass.pass_type.lessons == 1:
#                 buf['color'] = html_color_classes[c_lesson.group_pass.color]
#             else:
#                 buf['color'] = ORG_PASS_HTML_CLASS
#
#             try:
#                 c_lesson = lessons_itr.next()
#
#             except StopIteration:
#                 no_lessons = True
#
#         calendar.append(buf)
#
#     return calendar